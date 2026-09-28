import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="Customer Churn Analysis",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent


def load_data(candidates):
    """Load the first matching CSV/XLS/XLSX file.
    The uploaded .xls files in this project are CSV-formatted text,
    so they are also handled with read_csv.
    """
    for name in candidates:
        path = BASE_DIR / name
        if path.exists():
            try:
                return pd.read_excel(path, engine="xlrd")
            except Exception:
                try:
                    return pd.read_excel(path)
                except Exception:
                    pass
    raise FileNotFoundError(
        "Data file not found. Add the customer churn dataset to the "
        "Customer-Churn folder."
    )


@st.cache_data
def prepare_data():
    df = load_data([
        "customer_churn(1).xls",
    ])

    original = df.copy()

    df = df.drop(
        ["Names", "Location", "Company", "Onboard_date"],
        axis=1,
        errors="ignore"
    )

    # Same feature engineering used in the notebook
    df["Avg_Annual_Purchase"] = df["Total_Purchase"] / df["Years"]

    # Same IQR capping used in the notebook
    q1 = df["Total_Purchase"].quantile(0.25)
    q3 = df["Total_Purchase"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    df["Total_Purchase"] = np.where(
        df["Total_Purchase"] > upper_bound,
        upper_bound,
        np.where(df["Total_Purchase"] < lower_bound, lower_bound, df["Total_Purchase"])
    )

    return original, df


def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))


def cost_function(X, y, theta):
    m = len(y)
    h = np.clip(sigmoid(X.dot(theta)), 1e-15, 1 - 1e-15)
    error = y * np.log(h) + (1 - y) * np.log(1 - h)
    cost = -1 / m * np.sum(error)
    grad = 1 / m * X.T.dot(h - y)
    return cost, grad


def train_model(df):
    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    X_train_scaled = np.c_[np.ones((X_train_scaled.shape[0], 1)), X_train_scaled]
    X_test_scaled = np.c_[np.ones((X_test_scaled.shape[0], 1)), X_test_scaled]

    theta = np.zeros(X_train_scaled.shape[1])
    cost_history = np.zeros(1000)

    for i in range(1000):
        cost, grad = cost_function(
            X_train_scaled,
            y_train.to_numpy(),
            theta
        )
        theta -= 0.01 * grad
        cost_history[i] = cost

    probabilities = sigmoid(X_test_scaled.dot(theta))
    predictions = (probabilities > 0.5).astype(int)

    accuracy = np.mean(predictions == y_test.to_numpy())

    return theta, scaler, accuracy, cost_history


@st.cache_resource
def get_model():
    _, df = prepare_data()
    return train_model(df)


@st.cache_data
def load_new_customers():
    candidates = [
        "new_customers_1.xls",
    ]

    for name in candidates:
        path = BASE_DIR / name
        if path.exists():
            try:
                return pd.read_excel(path, engine="xlrd")
            except Exception:
                try:
                    return pd.read_excel(path)
                except Exception:
                    pass

    return None


# -----------------------------
# Load and train
# -----------------------------
try:
    original_df, df = prepare_data()
    theta, scaler, accuracy, cost_history = get_model()
except Exception as e:
    st.error(f"Unable to load the project data: {e}")
    st.stop()


# -----------------------------
# Header
# -----------------------------
st.title("📊 Customer Churn Analysis")
st.caption(
    "Exploratory analysis and a custom Logistic Regression model "
    "for identifying customers at risk of churn."
)

st.divider()


# -----------------------------
# KPI cards
# -----------------------------
total_customers = len(original_df)
churned_customers = int(original_df["Churn"].sum())
churn_rate = original_df["Churn"].mean() * 100
avg_purchase = original_df["Total_Purchase"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Customers", f"{total_customers:,}")
c2.metric("Churned Customers", f"{churned_customers:,}")
c3.metric("Churn Rate", f"{churn_rate:.1f}%")
c4.metric("Model Accuracy", f"{accuracy * 100:.1f}%")


# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

min_years = float(original_df["Years"].min())
max_years = float(original_df["Years"].max())

years_range = st.sidebar.slider(
    "Customer tenure (years)",
    min_value=min_years,
    max_value=max_years,
    value=(min_years, max_years)
)

account_options = sorted(original_df["Account_Manager"].dropna().unique().tolist())

selected_accounts = st.sidebar.multiselect(
    "Account Manager",
    options=account_options,
    default=account_options
)

filtered = original_df[
    original_df["Years"].between(years_range[0], years_range[1])
    & original_df["Account_Manager"].isin(selected_accounts)
].copy()


# -----------------------------
# Analysis
# -----------------------------
st.subheader("Customer Churn Overview")

left, right = st.columns(2)

with left:
    st.markdown("**Churn Distribution**")

    churn_counts = filtered["Churn"].value_counts().reindex([0, 1], fill_value=0)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Stayed", "Churned"], churn_counts.values)
    ax.set_ylabel("Customers")
    ax.set_title("Customer Churn Distribution")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.markdown("**Churn by Number of Sites**")

    site_churn = (
        filtered.groupby("Num_Sites")["Churn"]
        .mean()
        .mul(100)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(site_churn["Num_Sites"], site_churn["Churn"], marker="o")
    ax.set_xlabel("Number of Sites")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Churn Rate by Number of Sites")
    ax.grid(alpha=0.25)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


left, right = st.columns(2)

with left:
    st.markdown("**Churn by Account Manager**")

    manager_churn = (
        filtered.groupby("Account_Manager")["Churn"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(manager_churn.index.astype(str), manager_churn.values)
    ax.set_xlabel("Account Manager")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Churn Rate by Account Manager")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.markdown("**Total Purchase vs. Churn**")

    fig, ax = plt.subplots(figsize=(6, 4))
    for churn_value, label in [(0, "Stayed"), (1, "Churned")]:
        subset = filtered[filtered["Churn"] == churn_value]
        ax.scatter(
            subset["Years"],
            subset["Total_Purchase"],
            alpha=0.45,
            label=label
        )

    ax.set_xlabel("Years")
    ax.set_ylabel("Total Purchase")
    ax.set_title("Purchase and Tenure by Churn Status")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# -----------------------------
# Model section
# -----------------------------
st.divider()
st.subheader("🤖 Churn Prediction Model")

m1, m2 = st.columns(2)

with m1:
    st.metric("Test Set Accuracy", f"{accuracy * 100:.2f}%")
    st.write(
        "The model follows the same workflow as the notebook: "
        "feature engineering, IQR outlier capping, train/test split, "
        "standard scaling, and custom Logistic Regression using gradient descent."
    )

with m2:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(cost_history)
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Cost")
    ax.set_title("Gradient Descent Cost History")
    ax.grid(alpha=0.25)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# -----------------------------
# New customer predictions
# -----------------------------
st.divider()
st.subheader("🔎 New Customer Predictions")

new_customers = load_new_customers()

if new_customers is not None:
    prediction_df = new_customers.copy()

    model_input = new_customers.drop(
        ["Names", "Location", "Company", "Onboard_date"],
        axis=1,
        errors="ignore"
    ).copy()

    model_input["Avg_Annual_Purchase"] = (
        model_input["Total_Purchase"] / model_input["Years"]
    )

    # Match the notebook's feature preparation
    q1 = df["Total_Purchase"].quantile(0.25)
    q3 = df["Total_Purchase"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    model_input["Total_Purchase"] = np.where(
        model_input["Total_Purchase"] > upper_bound,
        upper_bound,
        np.where(
            model_input["Total_Purchase"] < lower_bound,
            lower_bound,
            model_input["Total_Purchase"]
        )
    )

    X_new = scaler.transform(model_input)
    X_new = np.c_[np.ones((X_new.shape[0], 1)), X_new]

    probabilities = sigmoid(X_new.dot(theta))
    predictions = (probabilities > 0.5).astype(int)

    prediction_df["Churn Probability"] = probabilities
    prediction_df["Prediction"] = np.where(
        predictions == 1,
        "Likely to Churn",
        "Likely to Stay"
    )

    prediction_df["Churn Probability"] = (
        prediction_df["Churn Probability"] * 100
    ).round(1)

    display_columns = [
        col for col in [
            "Names",
            "Age",
            "Total_Purchase",
            "Years",
            "Num_Sites",
            "Churn Probability",
            "Prediction"
        ]
        if col in prediction_df.columns
    ]

    st.dataframe(
        prediction_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "Add new_customers_1.csv to the Customer-Churn folder "
        "to display new customer predictions."
    )


st.caption(
    "Built with Python, Pandas, NumPy, Scikit-learn and Streamlit."
)
