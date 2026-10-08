# 📊 Data Jobs Dashboard

An interactive **Power BI dashboard** for analyzing the data-job market. The dashboard explores job demand, salaries, job posting trends, work-from-home opportunities, degree requirements, health insurance, job platforms, employment types, and geographic distribution.

The project provides both a **high-level market overview** and a **Job Title Drill Through** page for detailed analysis of individual data-related roles.

---

## ✨ Highlights

- 📊 Interactive analysis of the **data-job market**
- 💼 Compare job demand across different **job titles**
- 💰 Analyze **median yearly and hourly salaries**
- 📈 Track **job posting trends over time**
- 🏠 Analyze **work-from-home opportunities**
- 🎓 Analyze **degree requirements**
- 🏥 Explore **health insurance availability**
- 🌐 Compare jobs across different **job platforms**
- 💼 Analyze **employment/job types**
- 🌍 Compare job opportunities and salaries by **country**
- 🔎 Interactive **Job Title Drill Through** for detailed role-level analysis
- 📋 Tables with job statistics and trend sparklines

---

## 📊 Dashboard Overview

The dashboard consists of two main pages:

### 1. Data Jobs Dashboard

The main dashboard provides an overview of the data-job market.

#### Key KPIs

- **Job Count**
- **Median Yearly Salary**
- **Median Hourly Salary**
- **Average Job Rating**

A **Job Title slicer** allows users to filter the dashboard and analyze specific roles.

### Job Market Analysis

The main dashboard includes visualizations for:

- Job demand by job title
- Salary vs. job demand
- Job posting trends
- Job title comparisons
- Job statistics table
- Quarterly job-posting trends

---

### 2. 🔎 Job Title Drill Through

The drill-through page provides a detailed analysis of a selected job title.

Users can select a job title from the main dashboard and drill through to its dedicated analysis page.

The page includes:

- Salary analysis
- Work-from-home availability
- Degree requirements
- Health insurance
- Job platforms
- Employment types
- Country-level job analysis

---

## 💰 Salary Analysis

The dashboard analyzes both yearly and hourly compensation.

### Yearly Salary

For the selected job title, the dashboard provides:

- Minimum salary
- Maximum salary
- Average salary
- Median salary

### Hourly Salary

The dashboard also provides:

- Minimum hourly salary
- Maximum hourly salary
- Average hourly salary
- Median hourly salary

This allows users to compare compensation across different data-related roles.

---

## 🏠 Work From Home

The dashboard analyzes the availability of **work-from-home opportunities** within job postings.

This provides insight into how common remote opportunities are for different data-job roles.

---

## 🎓 Degree Requirements

The dashboard analyzes whether job postings mention a **degree requirement**.

This helps users understand the educational expectations associated with different data-related careers.

---

## 🏥 Health Insurance

The dashboard also analyzes the availability or mention of **health insurance** in job postings.

This provides additional insight into the benefits associated with different roles.

---

## 🌐 Job Platforms

Job postings are analyzed by the platform through which they were posted.

This helps identify which job platforms contain the largest number of opportunities for different data-related roles.

---

## 💼 Employment Types

The dashboard analyzes different employment types, including:

- Full-time
- Part-time
- Internship
- Contractor
- Temporary work

A treemap visualization is used to compare the distribution of different job types.

---

## 🌍 Geographic Analysis

The dashboard includes geographic analysis of job opportunities by country.

The map can be used to compare:

- Job count
- Median yearly salary
- Geographic distribution of opportunities

This provides insight into where data-related jobs are concentrated and how compensation varies between countries.

---

## 📈 Job Posting Trends

Job posting activity is analyzed over time using date-based trends.

The dashboard supports analysis across:

```text
Year
 └── Quarter
      └── Month
           └── Day
```

This makes it possible to identify changes in job demand over time.

---

## 🔎 Interactive Features

The dashboard includes several interactive Power BI features:

- Job Title slicers
- Cross-filtering
- Interactive charts
- Drill Through
- Geographic filtering
- KPI cards
- Tables
- Sparklines
- Tooltips

The **Drill Through** feature allows users to move from the overall job market into detailed analysis of a specific job title.

---

## 🧠 Business Questions Answered

The dashboard can help answer questions such as:

### Job Demand

- Which data-related jobs have the highest demand?
- How does job demand vary between different roles?
- How has job demand changed over time?

### Salary

- Which roles have the highest salaries?
- What is the median salary for a particular role?
- How do yearly and hourly salaries compare?

### Career Requirements

- Which jobs mention degree requirements?
- Which roles offer work-from-home opportunities?
- Which roles provide or mention health insurance?

### Employment

- What percentage of jobs are full-time?
- How common are internships and contract positions?
- Which platforms have the most job postings?

### Geography

- Which countries have the most data-job opportunities?
- How does salary vary by country?
- Where are particular job titles most common?

---

## 🗂️ Dashboard Structure

```text
Data Jobs Dashboard
│
├── 📊 Data Jobs Dashboard
│   ├── Job Count
│   ├── Median Yearly Salary
│   ├── Median Hourly Salary
│   ├── Average Job Rating
│   ├── Job Title Filter
│   ├── Salary vs Job Demand
│   ├── Job Title Comparison
│   ├── Job Posting Trends
│   └── Job Statistics Table
│
└── 🔎 Job Title Drill Through
    ├── Salary Analysis
    ├── Work From Home
    ├── Degree Requirements
    ├── Health Insurance
    ├── Job Platforms
    ├── Employment Type
    └── Country Analysis
```

---

## 🗃️ Data Model

The primary job-posting dataset used in the dashboard is:

```text
job_postings_flat
```

Important fields used for analysis include:

```text
job_title_short
job_posted_date
salary_year_avg
salary_hour_avg
job_country
job_schedule_type
job_via
job_health_insurance
```

These fields are used to analyze:

- Job demand
- Salary
- Job trends
- Geography
- Employment type
- Benefits
- Job platforms
- Remote opportunities

---

## 🛠️ Tech Stack

### Business Intelligence

- **Microsoft Power BI**
- **Power BI Desktop**

### Data Preparation & Analysis

- **Power Query**
- **DAX**
- **Data Modeling**

### Visualization

- KPI Cards
- Bar Charts
- Line Charts
- Scatter Charts
- Donut Charts
- Treemaps
- Maps
- Tables
- Sparklines
- Slicers
- Drill Through

---

## 📚 Skills Demonstrated

This project demonstrates practical experience with:

- Power BI
- Power Query
- DAX
- Data Cleaning
- Data Transformation
- Data Modeling
- KPI Development
- Data Visualization
- Interactive Dashboards
- Drill-Through Reports
- Time-Series Analysis
- Salary Analysis
- Geographic Analysis
- Business Intelligence
- Data Storytelling

---

## 🚀 How to Use

### Requirements

- Microsoft Power BI Desktop
- The `.pbix` dashboard file
- Access to the underlying dataset if the data needs to be refreshed

### Open the Dashboard

1. Download or clone this repository.
2. Open:

```text
Data Jobs Dashboard.pbix
```

3. Open the file using **Power BI Desktop**.
4. Use the **Job Title** slicer to filter the dashboard.
5. Explore the visualizations.
6. Select a job title and use **Drill Through** to open the detailed job-title analysis.

---

## 🔄 Analysis Workflow

```text
Raw Job Data
      ↓
Data Cleaning & Transformation
      ↓
Data Modeling
      ↓
DAX Measures
      ↓
Interactive Visualizations
      ↓
Data Jobs Dashboard
      ↓
Job Title Drill Through
      ↓
Detailed Career Analysis
```

---

## 🎯 Project Objective

The objective of this project is to transform raw job-posting data into an interactive **Business Intelligence dashboard** that helps users understand the data-job market.

Instead of analyzing individual job postings separately, the dashboard summarizes the market across key dimensions:

```text
Job Demand
Salary
Time
Location
Education
Benefits
Employment Type
Job Platform
Remote Work
```

This makes it easier to identify trends, compare job opportunities, and understand the characteristics of different data-related careers.

---

## 🔮 Future Improvements

- Add year-over-year job growth analysis
- Add salary percentile analysis
- Add salary growth trends
- Add company-level analysis
- Add industry-level analysis
- Add experience-level analysis
- Add dedicated remote-job analysis
- Add additional geographic filters
- Add bookmark-based navigation
- Create a mobile-optimized dashboard
- Publish the dashboard through Power BI Service

---

## 👤 Author

**Farooqui Mohd Maroof**

GitHub: [@MaroofBy](https://github.com/MaroofBy)

---

## 📌 Project Status

**Completed — Power BI Data Analytics & Business Intelligence Project**

An interactive Power BI dashboard for exploring the data-job market through job demand, salary, trends, benefits, employment type, job platforms, remote opportunities, and geographic analysis.
