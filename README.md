# 🍽️ Bangalore Restaurant Market Analysis — Zomato Data Analytics Project



## 📌 Table of Contents
- [Problem Statement](#-problem-statement)
- [Dataset Overview](#-dataset-overview)
- [Tech Stack](#-tech-stack)
- [Project Workflow](#-project-workflow)
- [Data Cleaning & EDA](#-data-cleaning--eda)
- [Business KPIs](#-business-kpis)
- [SQL Analysis — Queries & Business Significance](#-sql-analysis--queries--business-significance)
- [Dashboard](#-dashboard)
- [Key Insights](#-key-insights)
- [Project Structure](#-project-structure)


---

## 🎯 Problem Statement

Bangalore's restaurant industry is dense, fragmented, and highly competitive, spanning thousands of listings across dozens of localities, cuisines, and price bands. Restaurant owners, food-delivery platforms, and prospective investors lack a clear, data-backed view of:

- **Where** restaurant supply is concentrated and whether quality holds up under that density
- **Whether** operational choices (like offering home delivery) actually improve customer satisfaction
- **Which** cuisines truly drive customer engagement rather than simply having the most listings
- **Who** the top-performing restaurants are in each neighborhood
- **Where** the best value-for-money ("hidden gem") restaurants are hiding

This project cleans, explores, and analyzes a real-world Zomato restaurant dataset (Bangalore) to answer these questions and translate raw listing data into actionable business intelligence for restaurant owners, marketing teams, and platform strategists.

---

## 📊 Dataset Overview

| Attribute | Detail |
|---|---|
| **Source** | Zomato restaurant listings — Bangalore |
| **Raw Size** | ~8,921 restaurant records |
| **Grain** | One row per restaurant |
| **Key Raw Fields** | `Name`, `URL`, `Cuisines`, `Area`, `Timing`, `Full_Address`, `PhoneNumber`, `IsHomeDelivery`, `isTakeaway`, `isIndoorSeating`, `isVegOnly`, `Dinner Ratings`, `Dinner Reviews`, `Delivery Ratings`, `Delivery Reviews`, `KnownFor`, `PopularDishes`, `PeopleKnownFor`, `AverageCost` |
| **Engineered Fields** | `Locality`, `Primary_Cuisine`, `Dinner_Rating_Unavailable`, `Delivery_Rating_Unavailable`, `IsCostOutlier` |

---

## 🛠️ Tech Stack

| Layer | Tools Used |
|---|---|
| **Data Cleaning & EDA** | Python, Pandas, NumPy |
| **Visualization (EDA)** | Matplotlib, Seaborn |
| **Data Querying / Analysis** | SQL (window functions, CTEs, aggregate analytics) |
| **Notebook Environment** | Jupyter Notebook |
| **Dashboard** | Streamlit, Plotly|
| **Version Control** | Git & GitHub |

---

## 🔄 Project Workflow

```
Raw Zomato CSV
      │
      ▼
Data Cleaning & Feature Engineering (Python / Pandas)
      │
      ▼
Exploratory Data Analysis (Seaborn / Matplotlib)
      │
      ▼
SQL Analysis Layer (business questions → SQL queries)
      │
      ▼
Interactive Dashboard (Streamlit,Plotly,Pandas)
```

---

## 🧹 Data Cleaning & EDA

- **Column standardization** — trimmed/renamed inconsistent headers (e.g. `Dinner Ratings`, `Delivery Ratings`)
- **Locality extraction** — parsed the `Area` field into a clean `Locality` column for neighborhood-level analysis
- **Cuisine normalization** — derived a `Primary_Cuisine` field from the multi-value `Cuisines` string to enable clean group-bys
- **Missing rating handling** — flagged restaurants with no dinner/delivery ratings via `Dinner_Rating_Unavailable` and `Delivery_Rating_Unavailable` rather than silently dropping them
- **Cost outlier detection** — flagged extreme `AverageCost` values with `IsCostOutlier` to avoid skewing pricing analysis
- **Univariate & bivariate EDA** — distribution plots for cost and ratings, boxplots of average cost across the top 10 localities, and review-volume analysis across cuisines

### 📸 EDA Visuals




 Average Cost by Locality (Top 10) <img width="1500" height="900" alt="image" src="https://github.com/user-attachments/assets/53e3d578-1c36-439f-83af-440f1d5dc7b5" />
 
 Rating Distribution <img width="1800" height="750" alt="image" src="https://github.com/user-attachments/assets/2b61e5f1-0119-4a5a-afc1-a3140948cb25" />
 

---

## 📈 Business KPIs

| KPI | Description |
|---|---|
| **Restaurant Density per Locality** | Count of restaurants per locality — identifies supply concentration |
| **Average Cost for Two** | Core pricing KPI, tracked by locality and cuisine |
| **Top 3 Restaurants per Locality** | "Best-in-neighborhood" leaderboard, ranked by rating and review volume |
| **Value Score (Hidden Gems)** | Restaurants rated above their cuisine's average while priced below the cuisine's median cost |

---

## 🗃️ SQL Analysis — Queries & Business Significance

All queries run against the cleaned `zomato_restaurants` table.
### Q1 — Restaurant Density & Quality by Locality
```sql
SELECT locality, COUNT(*) AS restaurant_count,
       ROUND(AVG(dinner_rating), 2) AS avg_dinner_rating,
       ROUND(AVG(average_cost), 0) AS avg_cost_for_two_people
FROM zomato_restaurants
GROUP BY locality
ORDER BY restaurant_count DESC
LIMIT 15;
```
**Significance:** Surfaces where restaurant supply is most concentrated in Bangalore and whether average dining quality holds up under that competitive density — critical for site-selection and market-saturation decisions.

### Q2 — Home Delivery vs. Delivery Satisfaction
```sql
SELECT is_home_delivery, COUNT(*) AS restaurant_count,
       ROUND(AVG(delivery_rating), 2) AS avg_delivery_rating,
       ROUND(AVG(delivery_reviews), 0) AS avg_delivery_reviews
FROM zomato_restaurants
GROUP BY is_home_delivery;
```
**Significance:** Tests whether offering delivery genuinely improves customer satisfaction or whether delivery-enabled restaurants suffer lower ratings from operational strain — informs platform-level delivery policy and restaurant operations advice.

### Q3 — Cuisine Popularity by Review Volume
```sql
SELECT primary_cuisine, COUNT(*) AS listings,
       SUM(dinner_reviews + delivery_reviews) AS total_reviews,
       ROUND(AVG(average_cost), 0) AS avg_cost_for_two
FROM zomato_restaurants
GROUP BY primary_cuisine
ORDER BY total_reviews DESC
LIMIT 10;
```
**Significance:** Ranks cuisines by actual customer engagement (review volume) rather than raw listing count, alongside their price point — guides menu strategy, marketing spend, and new-outlet cuisine selection.

### Q4 — Top 3 Restaurants per Locality
```sql
WITH ranked AS (
    SELECT locality, name, dinner_rating, dinner_reviews,
           ROW_NUMBER() OVER (
               PARTITION BY locality
               ORDER BY dinner_rating DESC NULLS LAST, dinner_reviews DESC
           ) AS rank_in_locality
    FROM zomato_restaurants
    WHERE dinner_rating IS NOT NULL
)
SELECT locality, name, dinner_rating, dinner_reviews, rank_in_locality
FROM ranked
WHERE rank_in_locality <= 3
ORDER BY locality, rank_in_locality;
```
**Significance:** Produces a ready-to-use "best in neighborhood" leaderboard — directly deployable for a recommendation feature, local marketing push, or partnership prioritization.

### Q5 — Hidden Gems: Value-for-Money Outliers
```sql
WITH cuisine_stats AS (
    SELECT primary_cuisine,
           AVG(dinner_rating) AS cuisine_avg_rating,
           MEDIAN(average_cost) AS cuisine_median_cost
    FROM zomato_restaurants
    WHERE dinner_rating IS NOT NULL
    GROUP BY primary_cuisine
)
SELECT r.name, r.primary_cuisine, r.locality, r.dinner_rating, r.average_cost,
       cs.cuisine_avg_rating, cs.cuisine_median_cost
FROM zomato_restaurants r
JOIN cuisine_stats cs ON r.primary_cuisine = cs.primary_cuisine
WHERE r.dinner_rating > cs.cuisine_avg_rating
  AND r.average_cost < cs.cuisine_median_cost
ORDER BY r.dinner_rating DESC
LIMIT 25;
```
**Significance:** Flags restaurants that outperform their cuisine's average rating while staying below the median cost — a data-driven "hidden gem" finder for consumer recommendations and competitive benchmarking.

---

## 📊 Dashboard



### 🖼️ Dashboard Overview
<img width="1607" height="886" alt="image" src="https://github.com/user-attachments/assets/a6881b46-9c08-4de8-96dd-7f6ef7a2bbac" />




### 🖼️ Hidden Gems - high rating , low cost
<img width="1335" height="675" alt="image" src="https://github.com/user-attachments/assets/a546614f-7a58-41e1-82ca-2143ab337224" />



### 🖼️ Cuisine & Pricing Insights
<img width="1492" height="872" alt="image" src="https://github.com/user-attachments/assets/34a24545-fd27-4bf1-b60d-78fe4388c362" />


---
## 📌 Key Insights

- 🏙️ **Restaurant distribution is heavily concentrated in Bangalore's IT corridors**, with Electronic City, Marathahalli, HSR, and Whitefield accounting for the highest restaurant density, reflecting strong demand from working professionals.

- 🚚 **Home delivery has become the industry standard**, with over **99% of restaurants offering delivery**. Delivery-enabled restaurants receive **16× more customer reviews** on average, highlighting significantly higher customer engagement and online visibility.

- 🍛 **North Indian cuisine dominates the food landscape**, generating the highest customer engagement with **4.59 million reviews**, followed by **South Indian (2.59 million)** and **Biryani (2.48 million)**, making them the most popular cuisines in Bangalore.

- ⭐ **Top-rated restaurants are spread across multiple localities** rather than being concentrated in premium neighborhoods, indicating that exceptional dining experiences are available throughout the city.

- 💰 **Affordable South Indian restaurants consistently deliver outstanding customer satisfaction**, with several eateries achieving **4.8–4.9 ratings** while charging only **₹100–₹150 for two**, demonstrating that **value for money is a stronger driver of customer satisfaction than high pricing**.


## 📁 Project Structure

```
BANGALORE_ZOMATO_ANALYTICS_PROJECT/
│
├── .git/
├── .venv/
├── .gitignore
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   |── BangaloreZomatoData.csv
│   │  
│   │
│   └── processed/
│       └── BangaloreZomatoData_clean.csv
│
├── database/
│   ├── zomato.duckdb
│   ├── ddl_schema.sql
│   ├── analysis_queries.sql
│   └── queries_answers.txt
│
├── docs/
│   ├── dashboard/
│   │   ├── data_analytics_demo.mp4
│   │   ├── hidden_gems.png
│   │   ├── localities_with_most_restaurants.png
│   │   └── top_cuisines_by_volume.png
│   │
│   └── plots/
│       ├── 01_rating_distributions.png
│       └── cost_by_locality.png
│
├── notebooks/
│   └── data_cleaning_EDA.ipynb
│
├── src/
│   └── query_runner.py
│
└── streamlit_app/
    └── app.py

---

