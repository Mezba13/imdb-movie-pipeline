from movie import clean_raw_data,build_exploded_genre
import pandas as pd

def test_clean_raw_data_drops_invalid_year():
    fake_df = pd.DataFrame({
        'Series_Title': ['Movie A', 'Movie B', 'Movie C'],
        'Released_Year': [1994, 'PG', 2001],
        'Certificate': ['A', 'U', 'A']
    })
    result = clean_raw_data(fake_df)
    assert len(result) == 2
    assert 'Movie B' not in result['Series_Title'].values

def test_build_exploded_genre():
    fake_df = pd.DataFrame({
        'Series_Title': ['Movie A', 'Movie B'],
        'Released_Year': [1994, 2001],
        'Genre': ['Action, Comedy', 'Drama']
    })
    result = build_exploded_genre(fake_df)
    assert len(result) == 2
