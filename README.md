# IMDb Movie Data Pipeline

A small but complete ETL pipeline that ingests the IMDb Top 1000 Movies dataset, 
validates data quality, models it as a star schema in DuckDB, and supports safe 
incremental loading of new movies without duplicating or corrupting existing data.

## Why this project

I built this to practice core data engineering fundamentals end-to-end: data 
validation, dimensional modeling, idempotent loading, and testing — not just 
running a script once, but making it behave correctly when run repeatedly on 
changing data, the way a real pipeline would in production.

## Architecture

IMDb CSV (raw)
│
▼
clean_raw_data() ──► validates & fixes data quality issues
│
├──► build_fact_movies() ──► fact_movies (1 row per movie)
│ │
│ ▼
│ dim_director (unique directors)
│
└──► build_exploded_genre() ──► bridge_movies_genre
│
▼
dim_genre (unique genres)


**Star schema design:**
- `fact_movies` — one row per movie (title, year, runtime, rating, gross, director_id)
- `dim_director` — each movie has exactly one director → simple foreign key
- `dim_genre` + `bridge_movies_genre` — each movie can have *multiple* genres 
  (e.g. "The Godfather" is both Crime and Drama), so genres needed a separate 
  bridge table rather than a single foreign key, to avoid duplicating every 
  other column per genre.

## A real bug I found and fixed

While validating `Released_Year`, I discovered one row ("Apollo 13") had the 
string `'PG'` in the `Released_Year` column instead of a year — a genuine data 
quality issue in the source CSV, not a bug in my code. I added validation that 
detects, logs a warning, and safely drops any row where `Released_Year` isn't 
a valid number, rather than letting it silently corrupt downstream tables or 
crash the pipeline with an unclear error.

## Incremental loading

The pipeline is idempotent: running it again — even with a file containing a 
mix of existing and brand-new movies — will not create duplicate rows or shift 
the meaning of existing IDs. This is enforced with `UNIQUE` constraints and 
`ON CONFLICT DO NOTHING` on every table (`fact_movies`, `dim_genre`, 
`dim_director`, `bridge_movies_genre`), and verified with a real test: running 
the pipeline on a file with 2 existing + 2 new movies correctly added only the 
2 new ones.

## Tech stack

- Python 3.14, pandas
- DuckDB (embedded analytical database)
- pytest (unit tests)
- Python `logging` (INFO/WARNING/ERROR, console + file output)

## How to run

```bash
pip install -r requirements.txt
python movie.py
```

Expects `imdb_top_1000.csv` in the same folder. Logs to console and `pipeline.log`.

## Running tests

```bash
pytest test_movie.py
```

## Project structure

├── movie.py # pipeline: extract, clean, model, load
├── test_movie.py # unit tests
├── imdb_top_1000.csv # source data
├── requirements.txt
└── README.md


## What I'd add next

- Cloud deployment (e.g. BigQuery or Postgres) to support multiple users
- Orchestration with Airflow for scheduled runs
- More granular test coverage
