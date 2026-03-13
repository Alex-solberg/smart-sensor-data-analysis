from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / 'data' / 'reports' / 'summary.txt'


def _format_series(name: str, series: pd.Series) -> list[str]:
    return [
        f'{name}\n',
        f"{'-' * len(name)}\n",
        f'Min:  {series.min():.2f}\n',
        f'Max:  {series.max():.2f}\n',
        f'Mean: {series.mean():.2f}\n',
        f'Std:  {series.std():.2f}\n\n',
    ]


def run_analysis(df_raw: pd.DataFrame, df_clean: pd.DataFrame, report_path: str | Path = REPORT_PATH) -> None:
    """Write a concise project report with summary statistics."""
    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    removed_rows = len(df_raw) - len(df_clean)
    removed_pct = (removed_rows / len(df_raw) * 100.0) if len(df_raw) else 0.0

    lines: list[str] = []
    lines.append('SMART SENSOR PROJECT REPORT\n')
    lines.append('=' * 72 + '\n\n')

    lines.append('Dataset overview\n')
    lines.append('-' * 72 + '\n')
    lines.append(f'Rows in raw dataset:     {len(df_raw)}\n')
    lines.append(f'Rows in cleaned dataset: {len(df_clean)}\n')
    lines.append(f'Rows removed:            {removed_rows} ({removed_pct:.2f}%)\n')
    lines.append(f'Number of columns:       {len(df_clean.columns)}\n\n')

    numeric_columns = df_clean.select_dtypes(include='number').columns.tolist()
    if numeric_columns:
        lines.append('Descriptive statistics\n')
        lines.append('-' * 72 + '\n')
        lines.append(df_clean[numeric_columns].describe().round(3).to_string())
        lines.append('\n\n')

    if 'bmp_temp_c' in df_clean:
        lines.extend(_format_series('BMP280 temperature (°C)', df_clean['bmp_temp_c']))
    if 'dht_temp_c' in df_clean:
        lines.extend(_format_series('DHT22 temperature (°C)', df_clean['dht_temp_c']))
    if 'dht_hum_pct' in df_clean:
        lines.extend(_format_series('DHT22 humidity (%)', df_clean['dht_hum_pct']))
    if 'bmp_press_hpa' in df_clean:
        lines.extend(_format_series('BMP280 pressure (hPa)', df_clean['bmp_press_hpa']))
    if 'lux' in df_clean:
        lines.extend(_format_series('Light level (lux)', df_clean['lux']))

    if {'bmp_temp_c', 'dht_temp_c'}.issubset(df_clean.columns):
        temp_diff = df_clean['dht_temp_c'] - df_clean['bmp_temp_c']
        lines.extend(_format_series('Temperature difference (DHT22 - BMP280)', temp_diff))

    report_file.write_text(''.join(lines), encoding='utf-8')
    print(f'Report written to: {report_file}')
