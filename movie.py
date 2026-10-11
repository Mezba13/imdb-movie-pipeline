import duckdb
from pathlib import Path
import logging
from transform import clean_raw_data, build_fact_movies, build_exploded_genre, build_dim_genre, build_bridge_table, add_director_id, dim_director
from load import load_dim_genre_to_db, load_dim_director_to_db, load_fact_and_bridge_to_db,run_verification_query
from extract import load_data

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s',
                     handlers=[
                         logging.StreamHandler(),
                         logging.FileHandler("pipeline.log")
                     ])



if __name__ == "__main__":
    base_path = Path(__file__).parent
    path = base_path / "imdb_incremental_test.csv"
    conn = duckdb.connect(base_path / "movies.duckdb")
    df=load_data(path)
    df=clean_raw_data(df)
    fact_movies=build_fact_movies(df)
    df_genre=build_exploded_genre(df)
    dim_genre=build_dim_genre(df_genre)
    dim_genre_id=load_dim_genre_to_db(dim_genre, conn)
    df_director=dim_director(df)
    dim_director_id=load_dim_director_to_db(df_director, conn)
    bridge_df=build_bridge_table(df_genre, dim_genre_id)
    fact_movies=add_director_id(fact_movies, dim_director_id)
    load_fact_and_bridge_to_db(fact_movies, bridge_df, conn)
    result=run_verification_query(conn)
    logging.info(result)
    logging.info(fact_movies.head(20))
    conn.close()
