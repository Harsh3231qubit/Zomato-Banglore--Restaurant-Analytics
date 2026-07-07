import duckdb
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)

DB_FILE = "database\zomato.duckdb"
CSV_FILE = "data\processed\BangaloreZomatoData_clean.csv"
QUERIES_FILE = "database\\analysis_queries.sql"


# 1. Connect (creates zomato.duckdb if it doesn't exist yet)

con = duckdb.connect(DB_FILE)


# 2. Create the table directly from the cleaned CSV
#    (simpler than running the DDL file + a separate COPY step —
#    DuckDB infers types automatically from the CSV)

con.execute(f"""
    CREATE OR REPLACE TABLE zomato_restaurants AS
    SELECT
        row_number() OVER ()              AS restaurant_id,
        Name                                AS name,
        URL                                 AS url,
        Cuisines                            AS cuisines,
        Primary_Cuisine                     AS primary_cuisine,
        Area                                AS area,
        Locality                            AS locality,
        Timing                              AS timing,
        Full_Address                        AS full_address,
        PhoneNumber                         AS phone_number,
        IsHomeDelivery                      AS is_home_delivery,
        isTakeaway                          AS is_takeaway,
        isIndoorSeating                     AS is_indoor_seating,
        isVegOnly                           AS is_veg_only,
        "Dinner Ratings"                    AS dinner_rating,
        Dinner_Rating_Unavailable           AS dinner_rating_unavailable,
        "Dinner Reviews"                    AS dinner_reviews,
        "Delivery Ratings"                  AS delivery_rating,
        Delivery_Rating_Unavailable         AS delivery_rating_unavailable,
        "Delivery Reviews"                  AS delivery_reviews,
        KnownFor                            AS known_for,
        PopularDishes                       AS popular_dishes,
        PeopleKnownFor                      AS people_known_for,
        AverageCost                         AS average_cost,
        IsCostOutlier                       AS is_cost_outlier
    FROM read_csv_auto('{CSV_FILE}')
""")

row_count = con.execute("SELECT COUNT(*) FROM zomato_restaurants").fetchone()[0]
print(f"Loaded {row_count} rows into zomato_restaurants (in {DB_FILE})\n")


# 3. Read the 5 analysis queries from the .sql file and run each one

with open(QUERIES_FILE, "r") as f:
    sql_text = f.read()

# split on semicolons, drop empty/comment-only chunks
raw_blocks = [q.strip() for q in sql_text.split(";") if q.strip()]
queries = [q for q in raw_blocks if any(
    line.strip() and not line.strip().startswith("--")
    for line in q.splitlines()
)]

for i, query in enumerate(queries, start=1):
    print("=" * 70)
    print(f"QUERY {i}")
    print("=" * 70)
    df = con.execute(query).fetchdf()
    print(df.to_string(index=False))
    print()

con.close()
print(f"Done. Database saved at: {DB_FILE}")
