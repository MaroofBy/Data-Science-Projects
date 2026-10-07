"""
Sales Forecasting Dashboard
---------------------------
Flask app that loads historical order data, aggregates it to monthly sales,
trains a few forecasting models (time-based hold-out), and serves a modern
interactive dashboard plus a small JSON API.

Run locally:   python app.py
Production:    gunicorn app:app --bind 0.0.0.0:$PORT
"""

import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sales.csv"

TEST_MONTHS = 12          # hold-out window used to evaluate models
MIN_MONTHS = 24           # minimum months of history needed after filtering
MAX_HORIZON = 24
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

app = Flask(__name__)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    # The CSV is not UTF-8 encoded, so latin1 is used.
    df = pd.read_csv(DATA_PATH, encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df = df.dropna(subset=["Order Date", "Sales"]).sort_values("Order Date")
    return df.reset_index(drop=True)


DF = load_data()
ALL_MONTHS = pd.date_range(DF["Order Date"].min().to_period("M").to_timestamp(),
                           DF["Order Date"].max().to_period("M").to_timestamp(),
                           freq="MS")
REGIONS = sorted(DF["Region"].dropna().unique().tolist())
SEGMENTS = sorted(DF["Segment"].dropna().unique().tolist())


def filter_df(region: str, segment: str) -> pd.DataFrame:
    d = DF
    if region != "All":
        d = d[d["Region"] == region]
    if segment != "All":
        d = d[d["Segment"] == segment]
    return d


def monthly_series(d: pd.DataFrame) -> pd.Series:
    s = d.set_index("Order Date")["Sales"].resample("MS").sum()
    return s.reindex(ALL_MONTHS, fill_value=0.0)


# --------------------------------------------------------------------------
# Modelling
# --------------------------------------------------------------------------
def make_features(index: pd.DatetimeIndex, t_start: int) -> pd.DataFrame:
    """Trend index + calendar-month one-hot columns (deterministic features,
    so multi-step forecasts need no recursion)."""
    X = pd.DataFrame({"t": np.arange(t_start, t_start + len(index))}, index=index)
    for m in range(2, 13):
        X[f"m{m}"] = (index.month == m).astype(int)
    return X


def get_models() -> dict:
    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=300, min_samples_leaf=2, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=2, random_state=42),
    }


def score(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mask = y_true > 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100) \
        if mask.any() else float("nan")
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": mape,
        "r2": float(r2_score(y_true, y_pred)),
    }


def label(ts) -> str:
    return pd.Timestamp(ts).strftime("%Y-%m")


def clean(x, nd=2):
    x = float(x)
    return None if np.isnan(x) or np.isinf(x) else round(x, nd)


@lru_cache(maxsize=256)
def build_payload(region: str, segment: str, model_name: str, horizon: int) -> dict:
    d = filter_df(region, segment)
    series = monthly_series(d)

    if (series > 0).sum() < MIN_MONTHS:
        raise ValueError("Not enough history for this filter combination "
                         f"(need at least {MIN_MONTHS} active months).")

    n = len(series)
    y = series.values.astype(float)
    X = make_features(series.index, 0)
    X_train, X_test = X.iloc[:n - TEST_MONTHS], X.iloc[n - TEST_MONTHS:]
    y_train, y_test = y[:n - TEST_MONTHS], y[n - TEST_MONTHS:]

    # ---- evaluate all models on the hold-out window ----------------------
    results, holdout_preds = [], {}
    for name, mdl in get_models().items():
        mdl.fit(X_train, y_train)
        pred = np.clip(mdl.predict(X_test), 0, None)
        holdout_preds[name] = pred
        results.append({"model": name, **score(y_test, pred), "baseline": False})

    # seasonal-naive baseline: same month last year
    naive = y[n - 2 * TEST_MONTHS: n - TEST_MONTHS]
    results.append({"model": "Seasonal Naive (baseline)", **score(y_test, naive),
                    "baseline": True})

    ml_results = [r for r in results if not r["baseline"]]
    best = min(ml_results, key=lambda r: r["mae"])["model"]
    selected = best if model_name == "auto" else model_name
    if selected not in holdout_preds:
        selected = best

    # ---- refit on all data and forecast ----------------------------------
    final = get_models()[selected]
    final.fit(X, y)
    future_idx = pd.date_range(series.index[-1] + pd.offsets.MonthBegin(1),
                               periods=horizon, freq="MS")
    X_future = make_features(future_idx, n)
    fc = np.clip(final.predict(X_future), 0, None)

    sigma = next(r["rmse"] for r in results if r["model"] == selected)
    lower = np.clip(fc - 1.96 * sigma, 0, None)
    upper = fc + 1.96 * sigma

    # ---- KPIs --------------------------------------------------------------
    total_sales = float(d["Sales"].sum())
    total_profit = float(d["Profit"].sum())
    orders = int(d["Order ID"].nunique())
    yearly = d.groupby(d["Order Date"].dt.year).agg(sales=("Sales", "sum"),
                                                   profit=("Profit", "sum"))
    yoy = None
    if len(yearly) >= 2 and yearly["sales"].iloc[-2] > 0:
        yoy = (yearly["sales"].iloc[-1] / yearly["sales"].iloc[-2] - 1) * 100

    # compare against the same calendar months one year earlier (avoids the
    # seasonality distortion of comparing with the immediately preceding months)
    k = min(horizon, 12)
    same_period_last_year = float(y[n - 12: n - 12 + k].sum())
    fc_total = float(fc.sum())
    fc_vs_last = ((float(fc[:k].sum()) / same_period_last_year - 1) * 100
                  if same_period_last_year > 0 else None)

    # ---- breakdowns --------------------------------------------------------
    by_region = d.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    by_sub = d.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=True)
    seas = series.groupby(series.index.month).mean()

    peak_month = MONTH_NAMES[int(seas.idxmax()) - 1]
    low_month = MONTH_NAMES[int(seas.idxmin()) - 1]

    return {
        "filters": {"region": region, "segment": segment, "horizon": horizon},
        "selected_model": selected,
        "best_model": best,
        "kpis": {
            "total_sales": clean(total_sales),
            "total_profit": clean(total_profit),
            "profit_margin": clean(total_profit / total_sales * 100 if total_sales else 0),
            "orders": orders,
            "yoy": clean(yoy) if yoy is not None else None,
            "forecast_total": clean(fc_total),
            "forecast_vs_last": clean(fc_vs_last) if fc_vs_last is not None else None,
            "avg_monthly": clean(y.mean()),
        },
        "history": {
            "labels": [label(i) for i in series.index],
            "sales": [clean(v) for v in y],
        },
        "backtest": {
            "labels": [label(i) for i in X_test.index],
            "values": [clean(v) for v in holdout_preds[selected]],
        },
        "forecast": {
            "labels": [label(i) for i in future_idx],
            "values": [clean(v) for v in fc],
            "lower": [clean(v) for v in lower],
            "upper": [clean(v) for v in upper],
        },
        "metrics": [{k: (clean(v) if isinstance(v, float) else v)
                     for k, v in r.items()} for r in results],
        "seasonality": {"labels": MONTH_NAMES, "values": [clean(v) for v in seas.values]},
        "yearly": {
            "years": [int(i) for i in yearly.index],
            "sales": [clean(v) for v in yearly["sales"]],
            "profit": [clean(v) for v in yearly["profit"]],
        },
        "regions": {"labels": by_region.index.tolist(),
                    "values": [clean(v) for v in by_region.values]},
        "subcats": {"labels": by_sub.index.tolist(),
                    "values": [clean(v) for v in by_sub.values]},
        "insights": {"peak_month": peak_month, "low_month": low_month,
                     "date_range": f"{label(series.index[0])} to {label(series.index[-1])}"},
    }


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        regions=REGIONS,
        segments=SEGMENTS,
        models=list(get_models().keys()),
        max_horizon=MAX_HORIZON,
        n_rows=len(DF),
    )


@app.route("/api/dashboard")
def api_dashboard():
    region = request.args.get("region", "All")
    segment = request.args.get("segment", "All")
    model_name = request.args.get("model", "auto")
    try:
        horizon = int(request.args.get("horizon", 6))
    except ValueError:
        horizon = 6
    horizon = max(1, min(MAX_HORIZON, horizon))

    if region != "All" and region not in REGIONS:
        return jsonify(error="Unknown region"), 400
    if segment != "All" and segment not in SEGMENTS:
        return jsonify(error="Unknown segment"), 400

    try:
        return jsonify(build_payload(region, segment, model_name, horizon))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@app.route("/health")
def health():
    return jsonify(status="ok", rows=len(DF))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
