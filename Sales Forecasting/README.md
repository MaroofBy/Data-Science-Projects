# 📈 Sales Forecasting Dashboard

An end-to-end machine learning project that turns historical order data into a **monthly sales forecast**, served through a modern, interactive web dashboard built with **Flask**, **scikit-learn**, and **Chart.js**.

**Live demo:** `https://<your-service-name>.onrender.com` *(add your Render URL after deploying)*

---

## ✨ Features

- **Interactive dashboard** with dark / light theme, responsive layout, and animated charts
- **Filters** for region, customer segment, forecast model, and forecast horizon (1–24 months)
- **KPI cards**: total sales, profit and margin, orders, year-over-year growth, forecast total
- **Forecast chart** with actual history, a 12-month back-test, and an approx. 95% prediction range
- **Seasonality**, yearly performance, regional share, and sub-category breakdown charts
- **Model comparison table** (MAE, RMSE, MAPE, R²) with an automatic "best model" pick
- **Download the forecast** as CSV
- **JSON API** and `/health` endpoint, ready for Render

---

## 🧠 How the model works

1. Orders are aggregated to **monthly sales** (from `Order Date`).
2. Features are a **time trend** plus **calendar-month indicators** (captures growth and seasonality).
3. Three models are trained and compared on a **time-based hold-out** (the most recent 12 months are never used for training):
   - Linear Regression
   - Random Forest
   - Gradient Boosting
4. A **seasonal-naive baseline** (same month last year) is shown for honest comparison.
5. In *Auto* mode the model with the lowest hold-out MAE is selected, refit on all data, and used to forecast.
6. The shaded band is an approximate 95% range (forecast ± 1.96 × hold-out RMSE).

> With only 48 months of history, treat forecasts as directional, not exact. The baseline row in the comparison table makes this visible.

---

## 🗂️ Project structure

```
sales-forecasting/
├── app.py                # Flask app: data loading, models, API
├── templates/
│   └── index.html        # Dashboard UI (HTML + CSS + JS)
├── data/
│   └── sales.csv         # Historical orders dataset
├── notebook.ipynb        # Original exploration notebook
├── requirements.txt      # Python dependencies
├── render.yaml           # Render blueprint (optional one-click setup)
├── .python-version       # Python version for Render
└── README.md
```

---

## 🚀 Run locally

```bash
git clone https://github.com/MaroofBy/sales-forecasting.git
cd sales-forecasting

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>.

---

## ☁️ Deploy on Render

### Option A: Dashboard (manual)

1. Push this project to a GitHub repository.
2. On [render.com](https://render.com), click **New +** → **Web Service** and connect your repo.
3. Use these settings:

   | Setting | Value |
   | --- | --- |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120` |
   | Health Check Path | `/health` |
   | Instance Type | Free |

4. (Optional) Add the environment variable `PYTHON_VERSION` = `3.12.3`.
5. Click **Create Web Service**. After the build finishes, your dashboard is live at the `onrender.com` URL.

### Option B: Blueprint (`render.yaml`)

1. Push the repo to GitHub.
2. In Render, choose **New +** → **Blueprint** and select the repo.
3. Render reads `render.yaml` and creates the service automatically.

**Notes**

- Free instances sleep after inactivity, so the first request can take 30–60 seconds to wake up.
- The app uses 1 worker with 4 threads to stay within the free tier's memory limit.
- Every push to your main branch triggers an automatic redeploy.

---

## 🔌 API

| Endpoint | Description |
| --- | --- |
| `GET /` | Dashboard |
| `GET /api/dashboard` | All dashboard data as JSON |
| `GET /health` | Health check |

Query parameters for `/api/dashboard`:

| Param | Values | Default |
| --- | --- | --- |
| `region` | `All`, `Central`, `East`, `South`, `West` | `All` |
| `segment` | `All`, `Consumer`, `Corporate`, `Home Office` | `All` |
| `model` | `auto`, `Linear Regression`, `Random Forest`, `Gradient Boosting` | `auto` |
| `horizon` | `1`–`24` (months) | `6` |

Example:

```bash
curl "http://localhost:5000/api/dashboard?region=West&segment=Consumer&model=auto&horizon=12"
```

---

## 🛠️ Tech stack

Python · Flask · pandas · NumPy · scikit-learn · Gunicorn · Chart.js · HTML/CSS/JS · Render

---

## 📌 Dataset

`data/sales.csv` contains retail order records (2014–2017) with order, customer, location, product, sales, quantity, discount, and profit fields. The file is not UTF-8, so it is read with `latin1` encoding.

---

## 🔮 Possible improvements

- Add Prophet / SARIMA / Holt-Winters and compare them on the hold-out
- Rolling-origin cross-validation instead of a single hold-out split
- Add category / state level forecasting
- Cache trained models and persist them with `joblib`

---

## 👤 Author

**Farooqui Mohd Maroof** · [GitHub @MaroofBy](https://github.com/MaroofBy)

If you found this useful, consider giving the repo a ⭐
