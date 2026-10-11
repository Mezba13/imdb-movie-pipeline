
import logging
from pathlib import Path
import sys
import pandas as pd
logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s',
                     handlers=[
                         logging.StreamHandler(),
                         logging.FileHandler("pipeline.log")
                     ])

def load_data(path):
    if not Path(path).exists():
        logging.error(f"File not found: {path}")
        sys.exit(1)
    try:
        df=pd.read_csv(path)
    except:
        logging.error(f"Error loading data: {path}")
        sys.exit(1)
    return df