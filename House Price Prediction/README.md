# 🏠 House Price Prediction

An end-to-end machine learning project that predicts the sale price of homes in Ames, Iowa, from the **Ames Housing** dataset (the classic Kaggle regression problem). It covers exploratory analysis, data cleaning, model comparison and tuning, and a **live web app** where you can describe a house and get an instant estimate.

🔗 **Live demo:** https://data-science-projects-1-bwqv.onrender.com/ <!-- replace after deploying -->

> The free Render tier sleeps when idle, so the first visit may take about 30 seconds to wake up.

---

## ✨ Highlights

- **1,460 home sales**, 79 original features, cleaned and expanded to 268 model features
- **7 regressors compared**: Linear, Ridge, Lasso, Decision Tree, Random Forest, Gradient Boosting, KNN
- **Gradient Boosting tuned with GridSearchCV** and selected as the final model
- **R² ≈ 0.90** and **MAE ≈ $16K** on held-out homes the model never saw
- **Modern web app** with live predictions, a price range, neighborhood comparison, and dark/light themes

## 📊 Results

Measured on a 20% hold-out split (`random_state=42`).

| Metric | Value |
|---|---|
| R² | 0.904 |
| MAE | ≈ $16,100 |
| RMSE | ≈ $27,100 |

Best parameters from the grid search: `n_estimators=300`, `learning_rate=0.05`, `max_depth=5`.

## 🧠 Approach

1. **EDA** (`01_eda`): distributions, correlations, missing values and outliers.
2. **Cleaning and feature engineering** (`02_data_cleaning`):
   - In many columns a missing value means "feature absent" (no garage, no basement), so these are filled with `None`; the rest use median or mode.
   - New features: `HouseAge`, `RemodelAge`, `TotalSF`, `TotalBathrooms`, `TotalPorchSF`, `HasPool`, `HasGarage`, `HasFireplace`.
   - Categorical variables are one-hot encoded.
3. **Modeling** (`03_model_building`): model comparison, cross-validation, residual analysis and hyperparameter tuning.
4. **Deployment** (`app.py`): a Flask app that trains on startup and serves predictions through a JSON API and a single-page UI.

## 🖥️ The web app

The form asks for 18 key details (neighborhood, square footage, rooms, quality, year built and more). Everything else is filled with typical values from the dataset, using the same preprocessing as the notebooks.

Each estimate shows:
- the predicted price with a likely range (10th to 90th percentile of the model's errors)
- price per square foot and a comparison to the neighborhood median
- the factors the model weighs most

Prices are in **USD at 2010 market levels**, since that is what the dataset contains. This is an educational project, not a formal appraisal.

## 🗂️ Project structure

```
.
├── app.py                    # Flask app: training, inference, API
├── templates/
│   └── index.html            # Web UI
├── requirements.txt          # Python dependencies
├── train.csv                 # Ames Housing training data
├── house_price_cleaned.csv   # Output of the cleaning notebook
├── utils.py                  # Shared helpers for the notebooks
├── 01_eda.ipynb
├── 02_data_cleaning.ipynb
└── 03_model_building.ipynb
```

## 🚀 Run locally

```bash
git clone https://github.com/MaroofBy/<your-repo>.git
cd <your-repo>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py                    # opens on http://localhost:5000
```

To retrain and save the model ahead of time, run `python app.py --train`.

## ☁️ Deploy on Render

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Root Directory | the folder containing `app.py` (leave blank if it is the repo root) |
| Build Command | `pip install -r requirements.txt && python app.py --train` |
| Start Command | `gunicorn app:app --workers 1 --threads 4 --timeout 120` |
| Environment variable | `PYTHON_VERSION` = `3.12.7` |

## 🔌 API

`POST /api/predict` with a JSON body:

```json
{
  "neighborhood": "CollgCr",
  "lot_area": 9500,
  "first_floor_sf": 1100,
  "second_floor_sf": 900,
  "basement_sf": 1000,
  "bedrooms": 3,
  "full_baths": 2,
  "half_baths": 1,
  "total_rooms": 8,
  "fireplaces": 1,
  "overall_qual": 7,
  "overall_cond": 5,
  "kitchen_qual": "Gd",
  "exterior_qual": "Gd",
  "central_air": "Y",
  "year_built": 2003,
  "year_remodeled": 2003,
  "garage_cars": 2
}
```

Response:

```json
{ "ok": true, "price": 220527, "low": 188603, "high": 249680, "per_sqft": 110 }
```

`GET /health` returns the service status.

## 🛠️ Tech stack

Python · pandas · NumPy · scikit-learn · Flask · Gunicorn · HTML/CSS/JavaScript · Render

## 👤 Author

**Farooqui Mohd Maroof**: [GitHub @MaroofBy](https://github.com/MaroofBy)

## 📄 Data

[Ames Housing dataset](https://www.kaggle.com/c/house-prices-advanced-regression-techniques), compiled by Dean De Cock.
