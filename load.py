import pandas as pd
import duckdb
import logging


logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s',
                     handlers=[
                         logging.StreamHandler(),
                         logging.FileHandler("pipeline.log")
                     ])
def load_dim_director_to_db(dim_director, conn):
    
    conn.execute("create sequence if not exists director_id_seq start with 1;")
    
    conn.execute("""create table if not exists dim_director(
    director_id integer primary key 
    default nextval('director_id_seq'),
    director varchar(100),
    unique(director))""")
    conn.register("director_data",dim_director)
    conn.execute("""insert into dim_director(director) 
    select Director 
    from director_data
    on conflict (director) do nothing;""")
    result=conn.execute("select director_id,director from dim_director").fetchdf()
    return result

def load_dim_genre_to_db(dim_genre, conn):
    conn.execute("create sequence if not exists genre_id_seq start with 1;")
    conn.execute("""create table 
    if not exists dim_genre(
    genre_id integer primary key 
    default nextval('genre_id_seq'), 
    genre varchar(50),

    unique(genre)
    )""")
    conn.register("genre_data",dim_genre)
    conn.execute("""insert into dim_genre(genre) 
    select Genre 
    from genre_data
    on conflict (genre) do nothing;""")
    result=conn.execute("select genre_id,genre from dim_genre").fetchdf()
    return result

def load_fact_and_bridge_to_db(fact_movies, bridge_df, conn):
    conn.execute("""create sequence if not exists fact_movies_id_seq start with 1;""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_movies (
        movie_id INTEGER PRIMARY KEY
            DEFAULT nextval('fact_movies_id_seq'),

        Series_Title VARCHAR,
        Released_Year INTEGER,
        director_id INTEGER,
        Certificate VARCHAR,
        Runtime VARCHAR,
        IMDB_Rating DOUBLE,
        Meta_score DOUBLE,
        No_of_Votes INTEGER,
        Gross VARCHAR,

        UNIQUE (Series_Title, Released_Year))
        """)
    conn.register("fact_movies_data", fact_movies)
    conn.execute("""
        INSERT INTO fact_movies (
            Series_Title,
            Released_Year,
            director_id,
            Certificate,
            Runtime,
            IMDB_Rating,
            Meta_score,
            No_of_Votes,
            Gross
        )
        SELECT
            Series_Title,
            Released_Year,
            director_id,
            Certificate,
            Runtime,
            IMDB_Rating,
            Meta_score,
            No_of_Votes,
            Gross
        FROM fact_movies_data

        ON CONFLICT (Series_Title, Released_Year)
        DO NOTHING
        """)
    conn.register("bridge_data", bridge_df)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bridge_movies_genre(
        Series_Title VARCHAR,
        Released_Year INTEGER,
        Genre_id INTEGER,
        UNIQUE (Series_Title, Released_Year, Genre_id)
        )
    """)

    conn.execute("""insert into bridge_movies_genre(Series_Title, Released_Year, Genre_id)
    select Series_Title, Released_Year, genre_id
        from bridge_data
        on conflict (Series_Title, Released_Year, Genre_id) do nothing;""")

def run_verification_query(conn):
    f_result=conn.execute("""
        select fm.Series_Title, dg.genre_id, dg.genre,fm.Director_id
        from fact_movies fm
        join bridge_movies_genre bmg on fm.Series_Title = bmg.Series_Title
        and fm.Released_Year = bmg.Released_Year
        join dim_genre dg on bmg.genre_id = dg.genre_id
    """).fetchdf()
    count=conn.execute("select count(*) from fact_movies")
    logging.info(len(f_result))
    logging.info(f'total count: {count.fetchone()[0]}')
    return f_result