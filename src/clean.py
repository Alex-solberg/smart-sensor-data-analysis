from __future__ import annotations

from pathlib import Path

import pandas as pd

from load import RAW_DATA_PATH, load_csv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'sensors_clean.csv'
EXPECTED_COLUMNS = [
    'timestamp',
    'lux',
    'bmp_temp_c',
    'bmp_press_hpa',
    'dht_temp_c',
    'dht_hum_pct',
]
NUMERIC_COLUMNS = EXPECTED_COLUMNS[1:]
VALID_RANGES = {
    'lux': (0, 200000),
    'bmp_temp_c': (-40, 85),
    'bmp_press_hpa': (300, 1100),
    'dht_temp_c': (-40, 80),
    'dht_hum_pct': (0, 100),
}


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')


def clean_data(input_path: str | Path = RAW_DATA_PATH, output_path: str | Path = CLEAN_DATA_PATH) -> pd.DataFrame:
    """Clean raw sensor data and save a GitHub-ready processed dataset."""
    df = load_csv(input_path).copy()
    _validate_columns(df)

    df = df[EXPECTED_COLUMNS].copy()
    rows_before = len(df)

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    df = df.dropna(subset=NUMERIC_COLUMNS)
    df = df.sort_values('timestamp').drop_duplicates(subset='timestamp', keep='first')

    for column, (minimum, maximum) in VALID_RANGES.items():
        df = df[df[column].between(minimum, maximum)]

    df['temp_diff_c'] = df['dht_temp_c'] - df['bmp_temp_c']
    df['hour'] = df['timestamp'].dt.hour

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    rows_after = len(df)
    print(f'Cleaned dataset saved to: {output_file}')
    print(f'Rows before cleaning: {rows_before}')
    print(f'Rows after cleaning:  {rows_after}')
    print(f'Rows removed:         {rows_before - rows_after}')

    return df


if __name__ == '__main__':
    clean_data()
