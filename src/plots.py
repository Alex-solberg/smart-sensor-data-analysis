from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'sensors_clean.csv'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ROLLING_WINDOW = '60min'
RESAMPLE_WINDOW = '1min'
RATE_SMOOTHING_WINDOW = 5


def load_clean_data(path: str | Path = CLEAN_DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp']).sort_values('timestamp').set_index('timestamp')
    return df


def _prepare_time_series(series: pd.Series, resample_window: str = RESAMPLE_WINDOW) -> pd.Series:
    prepared = series.sort_index()
    if len(prepared) > 2000:
        prepared = prepared.resample(resample_window).mean()
    return prepared.dropna()


def _apply_datetime_axis(ax: plt.Axes) -> None:
    locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True, alpha=0.3)


def _save_figure(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=180, bbox_inches='tight')
    plt.close(fig)


def save_line_plot(df: pd.DataFrame, column: str, title: str, y_label: str, filename: str) -> None:
    series = _prepare_time_series(df[column])
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(series.index, series.values, linewidth=1.4)
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(y_label)
    _apply_datetime_axis(ax)
    _save_figure(fig, filename)


def save_two_line_plot(
    df: pd.DataFrame,
    column_one: str,
    column_two: str,
    label_one: str,
    label_two: str,
    title: str,
    y_label: str,
    filename: str,
) -> None:
    left = _prepare_time_series(df[column_one])
    right = _prepare_time_series(df[column_two])

    combined = pd.concat([left.rename(label_one), right.rename(label_two)], axis=1).dropna()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(combined.index, combined[label_one], label=label_one, linewidth=1.4)
    ax.plot(combined.index, combined[label_two], label=label_two, linewidth=1.4)
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(y_label)
    ax.legend()
    _apply_datetime_axis(ax)
    _save_figure(fig, filename)


def save_scatter_plot(df: pd.DataFrame, x_column: str, y_column: str, title: str, x_label: str, y_label: str, filename: str) -> None:
    scatter_df = df[[x_column, y_column]].dropna()
    if len(scatter_df) > 5000:
        scatter_df = scatter_df.sample(5000, random_state=42)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(scatter_df[x_column], scatter_df[y_column], s=10, alpha=0.5)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, alpha=0.3)
    _save_figure(fig, filename)


def save_hourly_average_plot(df: pd.DataFrame, column: str, title: str, y_label: str, filename: str) -> None:
    hourly = df.groupby(df.index.hour)[column].mean()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(hourly.index, hourly.values, marker='o', linewidth=1.6)
    ax.set_title(title)
    ax.set_xlabel('Hour of day')
    ax.set_ylabel(y_label)
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, alpha=0.3)
    _save_figure(fig, filename)


def save_rate_of_change_plot(df: pd.DataFrame, column: str, title: str, y_label: str, filename: str) -> None:
    series = _prepare_time_series(df[column], resample_window='1min')
    smoothed = series.rolling(RATE_SMOOTHING_WINDOW, min_periods=1).mean()
    rate = smoothed.diff()
    rate = rate.dropna()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(rate.index, rate.values, linewidth=1.3)
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(y_label)
    _apply_datetime_axis(ax)
    _save_figure(fig, filename)


def print_insights(df: pd.DataFrame) -> None:
    print('Project plots generated successfully.')
    for column, label in [
        ('lux', 'Light (lux)'),
        ('bmp_temp_c', 'BMP280 temperature (°C)'),
        ('dht_temp_c', 'DHT22 temperature (°C)'),
        ('dht_hum_pct', 'Humidity (%)'),
        ('bmp_press_hpa', 'Pressure (hPa)'),
    ]:
        max_time = df[column].idxmax()
        max_value = df[column].max()
        rolling_peak = df[column].rolling(ROLLING_WINDOW).mean().dropna()
        if not rolling_peak.empty:
            peak_time = rolling_peak.idxmax()
            peak_value = rolling_peak.max()
            print(f'{label}: max={max_value:.2f} at {max_time}, rolling peak={peak_value:.2f} around {peak_time}')
        else:
            print(f'{label}: max={max_value:.2f} at {max_time}')


def generate_plots(df: pd.DataFrame | None = None, output_dir: str | Path = OUTPUT_DIR) -> None:
    global OUTPUT_DIR
    OUTPUT_DIR = Path(output_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if df is None:
        df = load_clean_data()
    elif 'timestamp' in df.columns:
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp']).sort_values('timestamp').set_index('timestamp')
    else:
        df = df.sort_index()

    save_line_plot(df, 'lux', 'Light level over time', 'Lux', 'light_over_time.png')
    save_line_plot(df, 'bmp_temp_c', 'BMP280 temperature over time', '°C', 'bmp_temp_over_time.png')
    save_line_plot(df, 'dht_temp_c', 'DHT22 temperature over time', '°C', 'dht_temp_over_time.png')
    save_line_plot(df, 'dht_hum_pct', 'Humidity over time', '%', 'humidity_over_time.png')
    save_line_plot(df, 'bmp_press_hpa', 'Pressure over time', 'hPa', 'pressure_over_time.png')

    save_two_line_plot(
        df,
        'bmp_temp_c',
        'dht_temp_c',
        'BMP280',
        'DHT22',
        'Temperature comparison (BMP280 vs DHT22)',
        '°C',
        'temperature_compare.png',
    )

    save_line_plot(df, 'temp_diff_c', 'Temperature difference (DHT22 - BMP280)', '°C', 'temp_diff_over_time.png')
    save_rate_of_change_plot(df, 'bmp_temp_c', 'BMP280 temperature rate of change', 'Δ°C per minute', 'bmp_temp_rate_of_change.png')

    rolling = df[['lux', 'bmp_temp_c', 'dht_temp_c', 'dht_hum_pct', 'bmp_press_hpa']].rolling(ROLLING_WINDOW).mean()
    save_line_plot(rolling, 'lux', f'Light rolling mean ({ROLLING_WINDOW})', 'Lux', 'light_rolling.png')
    save_line_plot(rolling, 'bmp_temp_c', f'BMP280 rolling mean ({ROLLING_WINDOW})', '°C', 'bmp_temp_rolling.png')
    save_line_plot(rolling, 'dht_temp_c', f'DHT22 rolling mean ({ROLLING_WINDOW})', '°C', 'dht_temp_rolling.png')
    save_line_plot(rolling, 'dht_hum_pct', f'Humidity rolling mean ({ROLLING_WINDOW})', '%', 'humidity_rolling.png')
    save_line_plot(rolling, 'bmp_press_hpa', f'Pressure rolling mean ({ROLLING_WINDOW})', 'hPa', 'pressure_rolling.png')

    save_scatter_plot(df, 'lux', 'bmp_temp_c', 'Lux vs BMP280 temperature', 'Lux', '°C', 'scatter_lux_vs_bmp_temp.png')
    save_scatter_plot(df, 'lux', 'dht_temp_c', 'Lux vs DHT22 temperature', 'Lux', '°C', 'scatter_lux_vs_dht_temp.png')
    save_scatter_plot(df, 'lux', 'dht_hum_pct', 'Lux vs humidity', 'Lux', '%', 'scatter_lux_vs_humidity.png')

    save_hourly_average_plot(df, 'lux', 'Average light by hour', 'Lux', 'avg_light_by_hour.png')
    save_hourly_average_plot(df, 'bmp_temp_c', 'Average BMP280 temperature by hour', '°C', 'avg_bmp_temp_by_hour.png')
    save_hourly_average_plot(df, 'dht_temp_c', 'Average DHT22 temperature by hour', '°C', 'avg_dht_temp_by_hour.png')
    save_hourly_average_plot(df, 'dht_hum_pct', 'Average humidity by hour', '%', 'avg_humidity_by_hour.png')

    print_insights(df)
    print(f'Plots saved to: {OUTPUT_DIR}')


if __name__ == '__main__':
    generate_plots()
