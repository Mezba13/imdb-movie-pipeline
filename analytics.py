import logging
from pathlib import Path

def run_analytics(conn,sql_path):
    sql_text=Path(sql_path).read_text()
    queries=[q.strip() for q in sql_text.split(';') if q.strip()]
    results=[]

    for q in queries:
        df=conn.execute(q).fetchdf()
        logging.info(df.to_string(index=False) + "\n")
        results.append(df)
    return results