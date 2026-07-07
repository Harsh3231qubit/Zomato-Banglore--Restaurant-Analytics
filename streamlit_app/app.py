

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Zomato Bangalore Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#E23744"  # Zomato red

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .metric-card {{
        background: linear-gradient(135deg, #1c1f26 0%, #14161b 100%);
        border: 1px solid #2a2d35;
        border-radius: 12px;
        padding: 18px 20px;
    }}
    h1, h2, h3 {{ font-family: 'Trebuchet MS', sans-serif; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #1c1f26;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------
@st.cache_data(show_spinner="Loading restaurant data...")
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)

    rename_map = {
        "Name": "name", "URL": "url", "Cuisines": "cuisines",
        "Primary_Cuisine": "primary_cuisine", "Area": "area",
        "Locality": "locality", "Timing": "timing",
        "Full_Address": "full_address", "PhoneNumber": "phone_number",
        "IsHomeDelivery": "is_home_delivery", "isTakeaway": "is_takeaway",
        "isIndoorSeating": "is_indoor_seating", "isVegOnly": "is_veg_only",
        "Dinner Ratings": "dinner_rating",
        "Dinner_Rating_Unavailable": "dinner_rating_unavailable",
        "Dinner Reviews": "dinner_reviews",
        "Delivery Ratings": "delivery_rating",
        "Delivery_Rating_Unavailable": "delivery_rating_unavailable",
        "Delivery Reviews": "delivery_reviews",
        "KnownFor": "known_for", "PopularDishes": "popular_dishes",
        "PeopleKnownFor": "people_known_for", "AverageCost": "average_cost",
        "IsCostOutlier": "is_cost_outlier",
    }
    df = df.rename(columns=rename_map)
    df.insert(0, "restaurant_id", range(1, len(df) + 1))

    bool_cols = ["is_home_delivery", "is_takeaway", "is_indoor_seating", "is_veg_only",
                 "dinner_rating_unavailable", "delivery_rating_unavailable", "is_cost_outlier"]
    for c in bool_cols:
        if c in df.columns:
            df[c] = df[c].astype("boolean")

    for c in ["dinner_rating", "delivery_rating", "average_cost", "dinner_reviews", "delivery_reviews"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


st.sidebar.title("🍽️ Zomato Bangalore")
st.sidebar.caption("Restaurant Analytics Dashboard")

uploaded = st.sidebar.file_uploader("Upload cleaned CSV (optional)", type=["csv"])
default_path = "sql\BangaloreZomatoData_clean.csv"

try:
    df = load_data(uploaded if uploaded is not None else default_path)
except FileNotFoundError:
    st.error(
        f"Couldn't find **{default_path}**. Upload it using the sidebar uploader, "
        "or place it in the same folder as this app."
    )
    st.stop()

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.header("Filters")

localities = sorted(df["locality"].dropna().unique().tolist())
sel_localities = st.sidebar.multiselect("Locality", localities, default=[])

cuisines = sorted(df["primary_cuisine"].dropna().unique().tolist())
sel_cuisines = st.sidebar.multiselect("Primary Cuisine", cuisines, default=[])

cost_min, cost_max = int(df["average_cost"].min()), int(df["average_cost"].max())
sel_cost = st.sidebar.slider("Cost for two (₹)", cost_min, cost_max, (cost_min, cost_max))

veg_only = st.sidebar.checkbox("Veg only", value=False)
home_delivery_only = st.sidebar.checkbox("Home delivery only", value=False)

f = df.copy()
if sel_localities:
    f = f[f["locality"].isin(sel_localities)]
if sel_cuisines:
    f = f[f["primary_cuisine"].isin(sel_cuisines)]
f = f[(f["average_cost"] >= sel_cost[0]) & (f["average_cost"] <= sel_cost[1])]
if veg_only:
    f = f[f["is_veg_only"] == True]
if home_delivery_only:
    f = f[f["is_home_delivery"] == True]

st.sidebar.markdown(f"**{len(f):,}** restaurants match filters")

# ----------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------
st.title("Zomato Bangalore — Restaurant Analytics")
st.caption("Explore supply density, ratings, cuisines, and value across Bangalore's restaurant scene.")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Restaurants", f"{len(f):,}")
k2.metric("Avg Dinner Rating", f"{f['dinner_rating'].mean():.2f} ⭐" if len(f) else "—")
k3.metric("Avg Delivery Rating", f"{f['delivery_rating'].mean():.2f} ⭐" if len(f) else "—")
k4.metric("Avg Cost for Two", f"₹{f['average_cost'].mean():,.0f}" if len(f) else "—")
k5.metric("Localities", f"{f['locality'].nunique():,}")

st.divider()

# ----------------------------------------------------------------------
# Tabs — one per analysis
# ----------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📍 Locality Supply",
    "🚚 Delivery Impact",
    "🍜 Top Cuisines",
    "🏆 Best in Neighborhood",
    "💎 Hidden Gems",
    "📋 Explore Data",
])

# ---- Q1: Locality supply & quality ----
with tab1:
    st.subheader("Which localities have the most restaurants, and how does quality hold up?")
    q1 = (
        f.groupby("locality")
        .agg(restaurant_count=("restaurant_id", "count"),
             avg_dinner_rating=("dinner_rating", "mean"),
             avg_cost_for_two=("average_cost", "mean"))
        .round(2).reset_index()
        .sort_values("restaurant_count", ascending=False)
        .head(15)
    )
    c1, c2 = st.columns([3, 2])
    with c1:
        fig = px.bar(q1, x="restaurant_count", y="locality", orientation="h",
                      color="avg_dinner_rating", color_continuous_scale="RdYlGn",
                      labels={"restaurant_count": "Restaurant Count", "locality": "",
                              "avg_dinner_rating": "Avg Rating"},
                      title="Top 15 Localities by Restaurant Count")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=480)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(q1, use_container_width=True, hide_index=True)
    st.info("💡 High supply doesn't always mean lower quality — check whether the most saturated localities keep pace on rating.")

# ---- Q2: Home delivery vs rating ----
with tab2:
    st.subheader("Does offering home delivery correlate with better delivery ratings?")
    q2 = (
        f.groupby("is_home_delivery")
        .agg(restaurant_count=("restaurant_id", "count"),
             avg_delivery_rating=("delivery_rating", "mean"),
             avg_delivery_reviews=("delivery_reviews", "mean"))
        .round(2).reset_index()
    )
    q2["is_home_delivery"] = q2["is_home_delivery"].map({True: "Offers Delivery", False: "No Delivery"})
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(q2, x="is_home_delivery", y="avg_delivery_rating", color="is_home_delivery",
                      text="avg_delivery_rating", title="Avg Delivery Rating",
                      color_discrete_sequence=[PRIMARY, "#4CAF50"])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(q2, x="is_home_delivery", y="avg_delivery_reviews", color="is_home_delivery",
                       text="avg_delivery_reviews", title="Avg Delivery Reviews (volume)",
                       color_discrete_sequence=[PRIMARY, "#4CAF50"])
        fig2.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(q2, use_container_width=True, hide_index=True)

# ---- Q3: Top cuisines by review volume ----
with tab3:
    st.subheader("Top cuisines by review volume — engagement and pricing")
    q3 = f.copy()
    q3["total_reviews"] = q3["dinner_reviews"].fillna(0) + q3["delivery_reviews"].fillna(0)
    q3 = (
        q3.groupby("primary_cuisine")
        .agg(listings=("restaurant_id", "count"),
             total_reviews=("total_reviews", "sum"),
             avg_cost_for_two=("average_cost", "mean"))
        .round(0).reset_index()
        .sort_values("total_reviews", ascending=False)
        .head(10)
    )
    fig = px.scatter(q3, x="avg_cost_for_two", y="total_reviews", size="listings",
                      color="primary_cuisine", text="primary_cuisine",
                      title="Cuisine Popularity vs Price (bubble size = number of listings)",
                      labels={"avg_cost_for_two": "Avg Cost for Two (₹)", "total_reviews": "Total Reviews"})
    fig.update_traces(textposition="top center")
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(q3, use_container_width=True, hide_index=True)

# ---- Q4: Best in neighborhood ----
with tab4:
    st.subheader("Top 3 restaurants per locality, ranked by dinner rating")
    sel_locality_q4 = st.selectbox("Pick a locality to spotlight", ["All"] + localities)
    base = f[f["dinner_rating"].notna()].copy()
    base = base.sort_values(["locality", "dinner_rating", "dinner_reviews"], ascending=[True, False, False])
    base["rank_in_locality"] = base.groupby("locality").cumcount() + 1
    q4 = base[base["rank_in_locality"] <= 3][
        ["locality", "name", "dinner_rating", "dinner_reviews", "rank_in_locality"]
    ]
    if sel_locality_q4 != "All":
        q4 = q4[q4["locality"] == sel_locality_q4]
    st.dataframe(q4, use_container_width=True, hide_index=True, height=500)

# ---- Q5: Hidden gems ----
with tab5:
    st.subheader("Hidden gems: above-average rating, below-median cost, by cuisine")
    cs = (
        f[f["dinner_rating"].notna()]
        .groupby("primary_cuisine")
        .agg(cuisine_avg_rating=("dinner_rating", "mean"),
             cuisine_median_cost=("average_cost", "median"))
        .reset_index()
    )
    merged = f.merge(cs, on="primary_cuisine", how="left")
    gems = merged[
        (merged["dinner_rating"] > merged["cuisine_avg_rating"]) &
        (merged["average_cost"] < merged["cuisine_median_cost"])
    ][["name", "primary_cuisine", "locality", "dinner_rating", "average_cost",
       "cuisine_avg_rating", "cuisine_median_cost"]].round(2)
    gems = gems.sort_values("dinner_rating", ascending=False).head(25)
    fig = px.scatter(gems, x="average_cost", y="dinner_rating", color="primary_cuisine",
                      hover_name="name", size_max=12,
                      title="Hidden Gems — High Rating, Low Cost",
                      labels={"average_cost": "Cost for Two (₹)", "dinner_rating": "Dinner Rating"})
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(gems, use_container_width=True, hide_index=True)

# ---- Raw explorer ----
with tab6:
    st.subheader("Explore the filtered dataset")
    cols_to_show = st.multiselect(
        "Columns to display",
        options=list(f.columns),
        default=["name", "locality", "primary_cuisine", "dinner_rating",
                 "delivery_rating", "average_cost", "is_home_delivery", "is_veg_only"],
    )
    st.dataframe(f[cols_to_show] if cols_to_show else f, use_container_width=True, height=550)
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=f.to_csv(index=False).encode("utf-8"),
        file_name="zomato_filtered.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Built with Streamlit · Data: BangaloreZomatoData_clean.csv")
