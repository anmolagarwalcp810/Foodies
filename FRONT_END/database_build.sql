DROP TABLE IF EXISTS restaurants,cities,provinces,foodchains,categories CASCADE;
DROP MATERIALIZED VIEW IF EXISTS restaurant_categories;
DROP INDEX IF EXISTS city_index, province_index;
DROP TRIGGER IF EXISTS add_to_view_trigger ON restaurants;

CREATE TABLE restaurants (
  id  SERIAL  NOT NULL,
  dateadded TIMESTAMP,
  dateupdated TIMESTAMP,
  address TEXT NOT NULL,
  categories  INTEGER,
  city_id  BIGINT NOT NULL,
  country TEXT NOT NULL,
  keys  TEXT,
  latitude  FLOAT,
  longitude FLOAT,
  foodchain_id  BIGINT NOT NULL,
  postalcode  TEXT,
  province_id  BIGINT NOT NULL,
  sourceurls  TEXT,
  websites  TEXT,
  location  POINT,
  CONSTRAINT primary_key PRIMARY KEY (id,categories,dateupdated)
);

-- copy restaurants FROM 'E:/Restaurants_Data/restaurants.csv' delimiter '~' csv header;
\copy restaurants FROM '/home/anmol/IITD/Semester_6/COL362/Project/Work/Foodies/static/restaurants.csv' delimiter '~' csv header;

CREATE TABLE cities (
  city_id INTEGER PRIMARY KEY,
  city TEXT NOT NULL
);

-- copy cities FROM 'E:/Restaurants_Data/cities.csv' delimiter ',' csv header;
\copy cities FROM '/home/anmol/IITD/Semester_6/COL362/Project/Work/Foodies/static/cities.csv' delimiter ',' csv header;

CREATE TABLE foodchains (
  foodchain_id INTEGER PRIMARY KEY,
  foodchain TEXT NOT NULL
);

-- copy foodchains FROM 'E:/Restaurants_Data/foodchains.csv' delimiter ',' csv header;
\copy foodchains FROM '/home/anmol/IITD/Semester_6/COL362/Project/Work/Foodies/static/foodchains.csv' delimiter ',' csv header;

CREATE TABLE provinces (
  province_id INTEGER PRIMARY KEY,
  province TEXT NOT NULL
);

-- copy provinces FROM 'E:/Restaurants_Data/provinces.csv' delimiter ',' csv header;
\copy provinces FROM '/home/anmol/IITD/Semester_6/COL362/Project/Work/Foodies/static/provinces.csv' delimiter ',' csv header;

CREATE TABLE categories (
  category TEXT NOT NULL,
  category_id INTEGER PRIMARY KEY
);

-- copy categories FROM 'E:/Restaurants_Data/categories.csv' delimiter ',' csv header;
\copy categories FROM '/home/anmol/IITD/Semester_6/COL362/Project/Work/Foodies/static/categories.csv' delimiter ',' csv header;

CREATE MATERIALIZED VIEW restaurant_categories AS
SELECT DISTINCT id, array_agg(DISTINCT category) as categories FROM restaurants, categories
WHERE category_id=restaurants.categories GROUP BY id ORDER BY id;

-- system will automatically update the index when modified
CREATE INDEX city_index on restaurants (city_id);
CREATE INDEX province_index on restaurants (province_id);
CREATE INDEX foodchain_index on restaurants (foodchain_id);

-- CREATE OR REPLACE FUNCTION add_to_materialized_view() RETURNS TRIGGER AS $a$
--   BEGIN
--     DROP MATERIALIZED VIEW IF EXISTS restaurant_categories;
--     CREATE MATERIALIZED VIEW restaurant_categories AS
--     SELECT DISTINCT id, array_agg(DISTINCT category) as categories FROM restaurants, categories
--     WHERE category_id=restaurants.categories GROUP BY id ORDER BY id;
--     RETURN NEW;
--   END
-- $a$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_to_materialized_view() RETURNS TRIGGER AS $a$
  BEGIN
    REFRESH MATERIALIZED VIEW restaurant_categories;
    RETURN NEW;
  END
$a$ LANGUAGE plpgsql;


CREATE TRIGGER add_to_view_trigger AFTER INSERT ON restaurants
FOR EACH STATEMENT EXECUTE PROCEDURE add_to_materialized_view();
