-- Data Analysis — SQL Queries

-- ------------------------------------------------------------
-- Q1. Which localities have the most restaurants, and what is
--     their average dinner rating?
--     Business insight: where is restaurant supply concentrated,
--     and is quality holding up under that density?
-- ---------------------------------------------------------------
SELECT
    locality,
    COUNT(*)                           AS restaurant_count,
    ROUND(AVG(dinner_rating), 2)       AS avg_dinner_rating,
    ROUND(AVG(average_cost), 0)        AS avg_cost_for_two_people
FROM zomato_restaurants
GROUP BY locality
ORDER BY restaurant_count DESC
LIMIT 15;

-- ------------------------------------------------------------
-- Q2. Does offering home delivery correlate with a better or
--     worse delivery rating? 
--     Business insight: is delivery-enabled really paying off
--     in customer satisfaction, or are delivery ratings lower
--     under operational strain?
-- ------------------------------------------------------------
SELECT
    is_home_delivery,
    COUNT(*)                          AS restaurant_count,
    ROUND(AVG(delivery_rating), 2)    AS avg_delivery_rating,
    ROUND(AVG(delivery_reviews), 0)   AS avg_delivery_reviews
FROM zomato_restaurants
GROUP BY is_home_delivery;


-- ------------------------------------------------------------
-- Q3. What are the top 10 cuisines by review volume-weighted
--     popularity, and how do they price? 
--     Business insight: which cuisines drive the most engagement
--     (not just listing count) and at what price point.
-- ------------------------------------------------------------
SELECT
    primary_cuisine,
    COUNT(*)                                       AS listings,
    SUM(dinner_reviews + delivery_reviews)         AS total_reviews,
    ROUND(AVG(average_cost), 0)                    AS avg_cost_for_two
FROM zomato_restaurants
GROUP BY primary_cuisine
ORDER BY total_reviews DESC
LIMIT 10;


-- ------------------------------------------------------------
-- Q4. Rank restaurants within each locality by dinner rating,
--     surfacing the top 3 per locality.
--     Business insight: a "best in neighborhood" list — directly
--     usable for a recommendation feature or marketing push.
-- ------------------------------------------------------------
WITH ranked AS (
    SELECT
        locality,
        name,
        dinner_rating,
        dinner_reviews,
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


-- ------------------------------------------------------------
-- Q5. Cost-to-rating efficiency: for each cuisine, compare each
--     restaurant's rating against the cuisine's average rating,
--     to flag "above-average value" restaurants below median cost.

--     Business insight: identifies high-rated, lower-cost outliers
--     per cuisine — a "hidden gem" finder.
-- ------------------------------------------------------------
WITH cuisine_stats AS (
    SELECT
        primary_cuisine,
        AVG(dinner_rating)      AS cuisine_avg_rating,
        MEDIAN(average_cost)    AS cuisine_median_cost   --- median is robust compared to mean for pricing
    FROM zomato_restaurants
    WHERE dinner_rating IS NOT NULL
    GROUP BY primary_cuisine
)
SELECT
    r.name,
    r.primary_cuisine,
    r.locality,
    r.dinner_rating,
    r.average_cost,
    cs.cuisine_avg_rating,
    cs.cuisine_median_cost
FROM zomato_restaurants r
JOIN cuisine_stats cs ON r.primary_cuisine = cs.primary_cuisine
WHERE r.dinner_rating > cs.cuisine_avg_rating
  AND r.average_cost < cs.cuisine_median_cost
ORDER BY r.dinner_rating DESC
LIMIT 25;
