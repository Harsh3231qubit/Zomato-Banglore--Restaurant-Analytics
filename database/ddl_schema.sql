-- SQL Environment Setup — DDL


DROP TABLE IF EXISTS zomato_restaurants;

CREATE TABLE zomato_restaurants (
    restaurant_id            INTEGER PRIMARY KEY,   -- surrogate key, add via ROW_NUMBER on import
    name                      VARCHAR,
    url                       VARCHAR,
    cuisines                  VARCHAR,               -- full comma-separated list
    primary_cuisine           VARCHAR,               -- first cuisine listed (derived)
    area                      VARCHAR,
    locality                  VARCHAR,               -- derived: text before first comma in area
    timing                    VARCHAR,
    full_address              VARCHAR,
    phone_number              VARCHAR,
    is_home_delivery          BOOLEAN,
    is_takeaway               BOOLEAN,
    is_indoor_seating         BOOLEAN,
    is_veg_only               BOOLEAN,
    dinner_rating             DECIMAL(2,1),          -- NULL = not enough data (was "-")
    dinner_rating_unavailable BOOLEAN,                -- 1 if dinner_rating is NULL
    dinner_reviews            INTEGER,
    delivery_rating           DECIMAL(2,1),          -- NULL = not enough data (was "-")
    delivery_rating_unavailable BOOLEAN,
    delivery_reviews          INTEGER,
    known_for                 VARCHAR,
    popular_dishes            VARCHAR,
    people_known_for          VARCHAR,
    average_cost              INTEGER,                -- cost for two, INR
    is_cost_outlier           BOOLEAN
);

