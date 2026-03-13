from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / 'data' / 'raw' / 'sensors.csv'


def load_csv(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load a CSV file and parse the timestamp column when present."""
    csv_path = Path(path)
    df = pd.read_csv(csv_path)

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    return df
