# 📉 Customer Churn Prediction

A machine learning classification project that predicts whether a customer is likely to **churn (stop using a company's advertising service)** based on historical customer information.

The project covers data exploration, preprocessing, feature engineering, outlier handling, feature scaling, and the implementation of **Logistic Regression from scratch using NumPy**. The trained model is also tested on a separate set of new customers to simulate predictions on unseen future data.

🔗 Live demo: https://data-science-projects-wr65.onrender.com

---

## ✨ Highlights

- **900 historical customer records** used for model training and evaluation
- **6 predictive features** after preprocessing and feature engineering
- Implemented **Logistic Regression from scratch** without using `sklearn`'s LogisticRegression model
- Built the complete learning process using:
  - Sigmoid function
  - Logistic regression cost function
  - Gradient descent
  - Probability-based prediction
- Created an engineered feature: **Average Annual Purchase**
- Applied **IQR-based outlier capping** to `Total_Purchase`
- Applied **StandardScaler** for feature normalization
- Used an **80/20 train-test split**
- Achieved approximately **89.44% accuracy** on the held-out test set
- Tested the trained model on **6 new customers**
- Predicted **4 customers as likely to churn** and **2 as unlikely to churn**

---

## 📊 Results

The dataset was divided into an **80% training set and 20% test set** using `random_state=42`.

| Metric | Value |
|---|---:|
| Training Samples | 720 |
| Test Samples | 180 |
| Test Accuracy | **89.44%** |
| Gradient Descent Iterations | 1,000 |
| Learning Rate | 0.01 |
| Final Cost | ≈ 0.318 |

The model correctly classified approximately **89.44% of the customers in the held-out test set**.

> Accuracy is the primary evaluation metric used in this project. Additional metrics such as precision, recall, F1-score, ROC-AUC, and a confusion matrix could be added in future versions.

---

## 🧠 Machine Learning Approach

### 1. Data Preparation

The original customer dataset contains information such as:

- Customer age
- Total purchases
- Account manager assignment
- Years as a customer
- Number of websites
- Onboarding date
- Customer/company information
- Churn status

The following non-predictive columns were removed:

```text
Names
Location
Company
Onboard_date
```

These fields were excluded because they do not provide useful numerical signals for the model in its current form.

---

### 2. Feature Engineering

A new feature was created to capture the customer's average purchasing activity per year:

```text
Avg_Annual_Purchase = Total_Purchase / Years
```

This provides an additional measure of customer purchasing behavior and gives the model a more useful representation of customer activity.

---

### 3. Outlier Handling

The `Total_Purchase` feature was processed using the **Interquartile Range (IQR)** method.

The lower and upper bounds were calculated as:

```text
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

Values outside these boundaries were capped rather than completely removed.

This reduces the influence of extreme purchase values while preserving the customer records.

---

### 4. Feature Selection

After preprocessing and feature engineering, the model uses the following six features:

| Feature | Description |
|---|---|
| `Age` | Customer age |
| `Total_Purchase` | Total amount of advertising purchases |
| `Account_Manager` | Whether an account manager is assigned |
| `Years` | Number of years as a customer |
| `Num_Sites` | Number of websites using the service |
| `Avg_Annual_Purchase` | Average purchase amount per customer year |

The target variable is:

```text
Churn
```

where:

```text
0 = Customer does not churn
1 = Customer churns
```

---

## 🤖 Logistic Regression From Scratch

Instead of directly using a pre-built Logistic Regression implementation from scikit-learn, this project implements the core algorithm manually using **NumPy**.

### Sigmoid Function

The sigmoid function converts the model's output into a probability between 0 and 1:

```python
def sigmoid(z):
    return 1 / (1 + np.exp(-z))
```

### Cost Function

Binary cross-entropy/logistic loss is used to measure prediction error:

```python
def costFunction(X, y, theta):
    m = len(y)
    h = sigmoid(X.dot(theta))
    error = y * np.log(h) + (1-y) * np.log(1-h)

    cost = -1/m * sum(error)
    grad = 1/m * X.T.dot(h-y)

    return cost, grad
```

### Gradient Descent

The model parameters are optimized using gradient descent:

```python
theta, cost_history = gradientDescent(
    X_train,
    y_train,
    np.zeros(X_train.shape[1]),
    alpha=0.01,
    iterations=1000
)
```

The cost history is also plotted to observe the model's learning process over the training iterations.

---

## 🔬 Training Pipeline

The complete machine learning pipeline is:

```text
Raw Customer Data
       ↓
Remove Unnecessary Columns
       ↓
Feature Engineering
       ↓
Outlier Handling
       ↓
Train/Test Split
       ↓
Feature Scaling
       ↓
Add Intercept
       ↓
Logistic Regression
       ↓
Gradient Descent
       ↓
Prediction
       ↓
Accuracy Evaluation
```

---

## 🧪 Testing on New Customers

After training, the model is tested on a separate dataset containing **6 new customers**.

The exact same preprocessing and feature engineering steps are applied before making predictions.

### Predictions

| Customer | Prediction |
|---|---|
| Customer 1 | Not Churn |
| Customer 2 | Churn |
| Customer 3 | Churn |
| Customer 4 | Churn |
| Customer 5 | Not Churn |
| Customer 6 | Churn |

### Summary

```text
Predicted Churn     : 4
Predicted No Churn  : 2
Total New Customers : 6
```

This simulates how the model could be used to identify customers who may require additional attention from account managers.

---

## 🎯 Business Use Case

Customer churn can have a significant impact on a service-based business.

The model can help a company identify customers who are potentially at higher risk of leaving.

For example:

```text
Customer Data
      ↓
Churn Prediction
      ↓
Identify High-Risk Customers
      ↓
Assign Account Manager
      ↓
Customer Retention Strategy
```

The goal is not simply to predict churn, but to help the business **prioritize customers for proactive retention efforts**.

---

## 🗂️ Project Structure

```text
.
├── customerchurnn.ipynb       # Complete ML analysis and model development
├── customer_churn.csv         # Historical customer dataset
├── new_customers_1.csv        # New customers used for prediction
└── README.md                  # Project documentation
```

> The uploaded datasets in this project may use `.xls` filenames even though their underlying content is CSV-formatted. For the notebook workflow, they are read using `pandas.read_csv()`.

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/MaroofBy/<your-repository>.git
cd <your-repository>
```

### 2. Install dependencies

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

### 3. Start Jupyter Notebook

```bash
jupyter notebook
```

Open:

```text
customerchurnn.ipynb
```

and run the notebook cells from top to bottom.

---

## 🛠️ Tech Stack

**Programming Language**

- Python

**Data Analysis**

- pandas
- NumPy

**Machine Learning**

- Logistic Regression
- Gradient Descent
- Feature Scaling
- Train/Test Split
- Outlier Handling
- Feature Engineering

**Visualization**

- Matplotlib
- Seaborn

**Development**

- Jupyter Notebook

---

## 📚 Dataset

The project uses a customer churn dataset containing historical information about customers of an advertising service.

### Original Features

```text
Names
Age
Total_Purchase
Account_Manager
Years
Num_Sites
Onboard_date
Location
Company
Churn
```

The dataset contains **900 customer records**.

A separate dataset containing **6 new customers** is used to demonstrate prediction on unseen data.

---

## 💡 Key Learning Outcomes

This project demonstrates practical understanding of:

- Binary classification
- Logistic Regression mathematics
- Sigmoid activation
- Cost functions
- Gradient descent optimization
- Train/test splitting
- Feature scaling
- Feature engineering
- Outlier handling using IQR
- Model evaluation
- Making predictions on unseen data
- Translating machine learning predictions into a business use case

---

## 🔮 Future Improvements

Possible improvements include:

- Add confusion matrix visualization
- Add precision, recall, and F1-score
- Calculate ROC-AUC
- Plot ROC curve
- Compare Logistic Regression with Random Forest, XGBoost, and other classifiers
- Perform cross-validation
- Tune the decision threshold based on business requirements
- Save the trained model using `joblib`
- Build a Flask or Streamlit prediction interface
- Add customer churn probability instead of only `0/1` predictions
- Deploy the model as a live web application

---

## 👤 Author

**Farooqui Mohd Maroof**

GitHub: [@MaroofBy](https://github.com/MaroofBy)

---

## 📌 Project Status

**Completed — Machine Learning Prototype**

The current version focuses on building and understanding Logistic Regression from scratch and validating it on both held-out historical customers and new customer data.
