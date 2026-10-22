
-- Query 1: Number of movies per genre
SELECT
    dg.genre,
    COUNT(DISTINCT (fm.Series_Title, fm.Released_Year)) AS movie_count
FROM fact_movies AS fm
JOIN bridge_movies_genre AS bmg
    ON fm.Series_Title = bmg.Series_Title
    AND fm.Released_Year = bmg.Released_Year
JOIN dim_genre AS dg
    ON bmg.genre_id = dg.genre_id
GROUP BY dg.genre
ORDER BY movie_count DESC;


-- Query 2: Average IMDb rating per genre
SELECT
    dg.genre,
    ROUND(AVG(fm.IMDB_Rating), 2) AS avg_rating
FROM fact_movies AS fm
JOIN bridge_movies_genre AS bmg
    ON fm.Series_Title = bmg.Series_Title
    AND fm.Released_Year = bmg.Released_Year
JOIN dim_genre AS dg
    ON bmg.genre_id = dg.genre_id
GROUP BY dg.genre
ORDER BY avg_rating DESC;


-- Query 3: Highest-rated movie in each genre
WITH ranked_movies AS (
    SELECT
        dg.genre,
        fm.Series_Title,
        fm.Released_Year,
        fm.IMDB_Rating,
        ROW_NUMBER() OVER (
            PARTITION BY dg.genre
            ORDER BY fm.IMDB_Rating DESC,
                     fm.Series_Title ASC,
                     fm.Released_Year ASC
        ) AS rn
    FROM fact_movies AS fm
    JOIN bridge_movies_genre AS bmg
        ON fm.Series_Title = bmg.Series_Title
        AND fm.Released_Year = bmg.Released_Year
    JOIN dim_genre AS dg
        ON bmg.genre_id = dg.genre_id
)
SELECT
    genre,
    Series_Title,
    Released_Year,
    IMDB_Rating
FROM ranked_movies
WHERE rn = 1
ORDER BY genre;