
import logging
import pandas as pd
logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s',
                     handlers=[
                         logging.StreamHandler(),
                         logging.FileHandler("pipeline.log")
                     ])

def clean_raw_data(df):
    df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
    bad_rows = df[df['Released_Year'].isna()]
    
    if not bad_rows.empty:
            logging.warning(f"Invalid Released_Year values found in {len(bad_rows)} row(s):")

            logging.info(
                bad_rows[
                    ['Series_Title', 'Released_Year', 'Certificate']
                ].to_string(index=False)
            )

            logging.info(f"\nDropping {len(bad_rows)} invalid row(s).")

    df = df.dropna(
            subset=['Released_Year']
        )
    
    df['Released_Year'] = df['Released_Year'].astype(int)
    return df

def build_fact_movies(df):
    fact_movies = df[
    [
        'Series_Title',
        'Released_Year',
        'Certificate',
        'Runtime',
        'Director',
        'IMDB_Rating',
        'Meta_score',
        'No_of_Votes',
        'Gross'
    ]
    ].copy()
   
    return fact_movies

def build_exploded_genre(df):
    df_genre=df[['Series_Title','Released_Year','Genre']]
    df_genre['Genre']=df_genre['Genre'].str.split(',')
    df_genre=df_genre.explode('Genre')
    df_genre['Genre']=df_genre['Genre'].str.strip()
    return df_genre

def build_dim_genre(df_genre):
    dim_genre=df_genre[['Genre']].drop_duplicates(keep='first').reset_index(drop=True)
    return dim_genre

def dim_director(df):
    dim_director=df[['Director']].drop_duplicates(keep='first').reset_index(drop=True)
    return dim_director


def build_bridge_table(df_genre, dim_genre_id):
    df_genre = df_genre.merge(dim_genre_id, left_on='Genre', right_on='genre', how='left')
    df_genre=df_genre.drop(columns=['genre'])
    return df_genre

def add_director_id(fact_movies, dim_director_id):
    fact_movies = fact_movies.merge(
        dim_director_id,
        left_on='Director',
        right_on='director',
        how='left'
    )

    fact_movies = fact_movies.drop(
        columns=['Director', 'director']
    )

    return fact_movies