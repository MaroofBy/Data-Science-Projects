"""
HomeWorth - House Price Prediction web app (Flask)
--------------------------------------------------
Ames Housing dataset -> Gradient Boosting regressor (same preprocessing and
tuned hyper-parameters as notebooks 02 / 03) -> modern single-page UI.

Local run :  python app.py
Render    :  build  -> pip install -r requirements.txt && python app.py --train
             start  -> gunicorn app:app --workers 1 --threads 4 --timeout 120
"""
import os
import re
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_PATH = BASE_DIR / "artifacts" / "model.joblib"
SALE_YEAR = 2010  # latest year in the dataset; prices reflect that market

# Best params found by GridSearchCV in 03_model_building
GB_PARAMS = dict(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)

# In Ames a missing value in these columns means "feature absent"
NONE_MEANS_ABSENT = [
    "Alley", "BsmtQual", "BsmtCond", "BsmtExposure", "BsmtFinType1", "BsmtFinType2",
    "FireplaceQu", "GarageType", "GarageFinish", "GarageQual", "GarageCond",
    "PoolQC", "Fence", "MiscFeature", "MasVnrType",
]

NEIGHBORHOOD_NAMES = {
    "Blmngtn": "Bloomington Heights", "Blueste": "Bluestem", "BrDale": "Briardale",
    "BrkSide": "Brookside", "ClearCr": "Clear Creek", "CollgCr": "College Creek",
    "Crawfor": "Crawford", "Edwards": "Edwards", "Gilbert": "Gilbert",
    "IDOTRR": "Iowa DOT & Rail Road", "MeadowV": "Meadow Village", "Mitchel": "Mitchell",
    "NAmes": "North Ames", "NoRidge": "Northridge", "NPkVill": "Northpark Villa",
    "NridgHt": "Northridge Heights", "NWAmes": "Northwest Ames", "OldTown": "Old Town",
    "SWISU": "South & West of ISU", "Sawyer": "Sawyer", "SawyerW": "Sawyer West",
    "Somerst": "Somerset", "StoneBr": "Stone Brook", "Timber": "Timberland",
    "Veenker": "Veenker",
}

FEATURE_LABELS = {
    "OverallQual": "Overall quality", "TotalSF": "Total square footage",
    "GrLivArea": "Above-ground living area", "GarageCars": "Garage capacity",
    "GarageArea": "Garage size", "TotalBathrooms": "Bathrooms",
    "Neighborhood": "Neighborhood", "KitchenQual": "Kitchen quality",
    "ExterQual": "Exterior quality", "YearBuilt": "Year built", "HouseAge": "House age",
    "TotalBsmtSF": "Basement size", "1stFlrSF": "First-floor area",
    "2ndFlrSF": "Second-floor area", "LotArea": "Lot size", "Fireplaces": "Fireplaces",
    "BsmtQual": "Basement quality", "FireplaceQu": "Fireplace quality",
    "YearRemodAdd": "Remodel year", "RemodelAge": "Years since remodel",
    "BsmtFinSF1": "Finished basement", "OverallCond": "Overall condition",
    "TotRmsAbvGrd": "Room count", "CentralAir": "Central air",
    "MSSubClass": "Dwelling type", "GarageType": "Garage type",
    "GarageFinish": "Garage finish", "LotFrontage": "Street frontage",
    "OpenPorchSF": "Open porch", "WoodDeckSF": "Wood deck", "BsmtExposure": "Basement exposure",
}


# --------------------------------------------------------------------------- #
# Data + feature engineering (mirrors utils.py so results match the notebooks)
# --------------------------------------------------------------------------- #
def find_data_file(name):
    for p in (BASE_DIR / "data" / name, BASE_DIR / name):
        if p.exists():
            return p
    raise FileNotFoundError(f"{name} not found. Put it next to app.py or in a data/ folder.")


def engineer(df):
    df = df.copy()
    df["HouseAge"] = df["YrSold"] - df["YearBuilt"]
    df["RemodelAge"] = df["YrSold"] - df["YearRemodAdd"]
    df["TotalSF"] = df["TotalBsmtSF"] + df["1stFlrSF"] + df["2ndFlrSF"]
    df["TotalBathrooms"] = (
        df["FullBath"] + df["BsmtFullBath"] + 0.5 * (df["HalfBath"] + df["BsmtHalfBath"])
    )
    df["TotalPorchSF"] = (
        df["OpenPorchSF"] + df["EnclosedPorch"] + df["3SsnPorch"] + df["ScreenPorch"]
    )
    df["HasPool"] = (df["PoolArea"] > 0).astype(int)
    df["HasGarage"] = (df["GarageArea"] > 0).astype(int)
    df["HasFireplace"] = (df["Fireplaces"] > 0).astype(int)
    return df


def pretty(name):
    if name in FEATURE_LABELS:
        return FEATURE_LABELS[name]
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)


# --------------------------------------------------------------------------- #
# Training
# --------------------------------------------------------------------------- #
def build_artifact():
    raw = pd.read_csv(find_data_file("train.csv")).drop(columns=["Id"], errors="ignore")
    y = raw["SalePrice"].astype(float)
    base = raw.drop(columns="SalePrice")

    for col in NONE_MEANS_ABSENT:
        if col in base:
            base[col] = base[col].fillna("None")

    num_cols = [c for c in base.columns if pd.api.types.is_numeric_dtype(base[c])]
    cat_cols = [c for c in base.columns if c not in num_cols]
    defaults = {c: float(base[c].median()) for c in num_cols}
    defaults.update({c: base[c].mode().iloc[0] for c in cat_cols})
    base = base.fillna(defaults)

    full = pd.get_dummies(engineer(base), columns=cat_cols, drop_first=True)
    X = full.astype(float)
    feature_cols = X.columns.tolist()

    # Honest hold-out metrics (same split as the notebook)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    holdout = GradientBoostingRegressor(**GB_PARAMS).fit(Xtr, ytr)
    pred = holdout.predict(Xte)
    ratio = (yte.values / pred)
    metrics = {
        "r2": float(r2_score(yte, pred)),
        "mae": float(mean_absolute_error(yte, pred)),
        "rmse": float(np.sqrt(mean_squared_error(yte, pred))),
        "ratio_lo": float(np.quantile(ratio, 0.10)),
        "ratio_hi": float(np.quantile(ratio, 0.90)),
        "n_train": int(len(X)),
    }

    # Final model uses every row
    model = GradientBoostingRegressor(**GB_PARAMS).fit(X, y)

    # Feature importance, collapsing one-hot columns back into their source column
    dummy_to_cat = {}
    for cat in cat_cols:
        for val in base[cat].unique():
            dummy_to_cat[f"{cat}_{val}"] = cat
    grouped = {}
    for name, imp in zip(feature_cols, model.feature_importances_):
        key = dummy_to_cat.get(name, name)
        grouped[key] = grouped.get(key, 0.0) + float(imp)
    top = sorted(grouped.items(), key=lambda kv: kv[1], reverse=True)[:7]
    drivers = [{"label": pretty(k), "weight": round(v / top[0][1], 4)} for k, v in top]

    # Neighborhood price table (sorted cheapest -> priciest)
    nb = raw.groupby("Neighborhood")["SalePrice"].agg(["median", "count"]).sort_values("median")
    neighborhoods = [
        {
            "code": code,
            "name": NEIGHBORHOOD_NAMES.get(code, code),
            "median": float(r["median"]),
            "count": int(r["count"]),
        }
        for code, r in nb.iterrows()
    ]

    garage_area = (
        raw.assign(GarageArea=raw["GarageArea"].fillna(0))
        .groupby("GarageCars")["GarageArea"].median().to_dict()
    )

    return {
        "model": model,
        "feature_cols": feature_cols,
        "cat_cols": cat_cols,
        "defaults": defaults,
        "metrics": metrics,
        "drivers": drivers,
        "neighborhoods": neighborhoods,
        "garage_area": {int(k): float(v) for k, v in garage_area.items()},
        "price_range": [float(y.min()), float(y.max())],
    }


def load_or_train():
    if ARTIFACT_PATH.exists():
        try:
            return joblib.load(ARTIFACT_PATH)
        except Exception as exc:  # e.g. library version mismatch -> retrain
            print(f"[warn] could not load saved model ({exc}); retraining")
    art = build_artifact()
    try:
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(art, ARTIFACT_PATH, compress=3)
    except OSError as exc:
        print(f"[warn] could not save model: {exc}")
    return art


# --------------------------------------------------------------------------- #
# Inference
# --------------------------------------------------------------------------- #
def row_to_vector(row, art):
    """Turn one complete raw-feature dict into the model's feature vector."""
    df = engineer(pd.DataFrame([row]))
    vec = {c: 0.0 for c in art["feature_cols"]}
    for c in df.columns:
        if c in vec:
            vec[c] = float(df.at[0, c])
    for cat in art["cat_cols"]:
        name = f"{cat}_{row[cat]}"
        if name in vec:
            vec[name] = 1.0
    return pd.DataFrame([vec], columns=art["feature_cols"])


INT_FIELDS = {  # key: (low, high, label)
    "lot_area": (1300, 215000, "Lot area"),
    "first_floor_sf": (300, 5000, "First-floor area"),
    "second_floor_sf": (0, 2500, "Second-floor area"),
    "basement_sf": (0, 6200, "Basement area"),
    "bedrooms": (0, 8, "Bedrooms"),
    "full_baths": (0, 4, "Full bathrooms"),
    "half_baths": (0, 3, "Half bathrooms"),
    "total_rooms": (2, 14, "Total rooms"),
    "fireplaces": (0, 4, "Fireplaces"),
    "overall_qual": (1, 10, "Overall quality"),
    "overall_cond": (1, 9, "Overall condition"),
    "year_built": (1872, SALE_YEAR, "Year built"),
    "year_remodeled": (1950, SALE_YEAR, "Remodel year"),
    "garage_cars": (0, 4, "Garage capacity"),
}
CHOICES = {
    "kitchen_qual": ["Ex", "Gd", "TA", "Fa"],
    "exterior_qual": ["Ex", "Gd", "TA", "Fa"],
    "central_air": ["Y", "N"],
}


def parse_payload(data, art):
    errors, clean = [], {}
    for key, (lo, hi, label) in INT_FIELDS.items():
        try:
            val = int(round(float(data.get(key))))
        except (TypeError, ValueError):
            errors.append(f"{label} must be a number.")
            continue
        if not lo <= val <= hi:
            errors.append(f"{label} must be between {lo:,} and {hi:,}.")
        clean[key] = val
    for key, options in CHOICES.items():
        val = data.get(key)
        if val not in options:
            errors.append(f"Invalid value for {key.replace('_', ' ')}.")
        clean[key] = val
    codes = {n["code"] for n in art["neighborhoods"]} | {"Blmngtn"}
    if data.get("neighborhood") not in codes:
        errors.append("Please choose a neighborhood.")
    clean["neighborhood"] = data.get("neighborhood")
    return clean, errors


def estimate(inp, art):
    d = art["defaults"]
    row = dict(d)
    f1, f2, bs = inp["first_floor_sf"], inp["second_floor_sf"], inp["basement_sf"]
    built = inp["year_built"]
    remod = max(inp["year_remodeled"], built)
    cars = inp["garage_cars"]

    row.update({
        "Neighborhood": inp["neighborhood"], "LotArea": inp["lot_area"],
        "1stFlrSF": f1, "2ndFlrSF": f2, "TotalBsmtSF": bs, "GrLivArea": f1 + f2,
        "BedroomAbvGr": inp["bedrooms"], "FullBath": inp["full_baths"],
        "HalfBath": inp["half_baths"], "TotRmsAbvGrd": inp["total_rooms"],
        "Fireplaces": inp["fireplaces"], "OverallQual": inp["overall_qual"],
        "OverallCond": inp["overall_cond"], "KitchenQual": inp["kitchen_qual"],
        "ExterQual": inp["exterior_qual"], "CentralAir": inp["central_air"],
        "YearBuilt": built, "YearRemodAdd": remod, "YrSold": SALE_YEAR,
        "GarageCars": cars, "GarageArea": art["garage_area"].get(cars, d["GarageArea"]),
        "MSSubClass": 60 if f2 > 0 else 20,
        "HouseStyle": "2Story" if f2 > 0 else "1Story",
        "FireplaceQu": "Gd" if inp["fireplaces"] > 0 else "None",
    })
    if cars > 0:
        row["GarageYrBlt"] = built
    else:
        row.update(GarageType="None", GarageFinish="None", GarageQual="None", GarageCond="None")
    if bs == 0:
        row.update(BsmtQual="None", BsmtCond="None", BsmtExposure="None",
                   BsmtFinType1="None", BsmtFinType2="None",
                   BsmtFinSF1=0, BsmtFinSF2=0, BsmtUnfSF=0)
    else:
        row.update(BsmtFinSF1=round(bs * 0.5), BsmtFinSF2=0, BsmtUnfSF=bs - round(bs * 0.5))

    price = float(art["model"].predict(row_to_vector(row, art))[0])
    price = max(price, 20000.0)
    m = art["metrics"]
    nb = next((n for n in art["neighborhoods"] if n["code"] == inp["neighborhood"]), None)
    living = f1 + f2
    return {
        "price": round(price),
        "low": round(price * m["ratio_lo"]),
        "high": round(price * m["ratio_hi"]),
        "per_sqft": round(price / living) if living else None,
        "living_sf": living,
        "neighborhood": {
            "name": nb["name"] if nb else inp["neighborhood"],
            "median": nb["median"] if nb else None,
            "delta_pct": round((price / nb["median"] - 1) * 100, 1) if nb else None,
        },
    }


# --------------------------------------------------------------------------- #
# Flask app
# --------------------------------------------------------------------------- #
app = Flask(__name__)
ART = load_or_train()


def public_meta():
    nbs = [dict(n) for n in ART["neighborhoods"]]
    if not any(n["code"] == "Blmngtn" for n in nbs):  # baseline category of drop_first
        nbs.insert(0, {"code": "Blmngtn", "name": NEIGHBORHOOD_NAMES["Blmngtn"],
                       "median": None, "count": 0})
    return {
        "neighborhoods": nbs,
        "drivers": ART["drivers"],
        "metrics": ART["metrics"],
        "sale_year": SALE_YEAR,
    }


@app.get("/")
def index():
    return render_template("index.html", meta=public_meta())


@app.post("/api/predict")
def predict():
    data = request.get_json(silent=True) or {}
    clean, errors = parse_payload(data, ART)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    try:
        return jsonify({"ok": True, **estimate(clean, ART)})
    except Exception as exc:  # pragma: no cover
        app.logger.exception("prediction failed")
        return jsonify({"ok": False, "errors": ["Prediction failed. Please try again."]}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok", "r2": round(ART["metrics"]["r2"], 4)})


if __name__ == "__main__":
    if "--train" in sys.argv:
        art = build_artifact()
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(art, ARTIFACT_PATH, compress=3)
        m = art["metrics"]
        print(f"Model saved -> {ARTIFACT_PATH}")
        print(f"Hold-out  R2={m['r2']:.4f}  MAE=${m['mae']:,.0f}  RMSE=${m['rmse']:,.0f}")
    else:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
