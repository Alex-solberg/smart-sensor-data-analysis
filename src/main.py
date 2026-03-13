from __future__ import annotations

from pathlib import Path

from analyze import run_analysis
from clean import CLEAN_DATA_PATH, clean_data
from load import RAW_DATA_PATH, load_csv
from plots import generate_plots


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
REPORT_PATH = PROJECT_ROOT / 'data' / 'reports' / 'summary.txt'


def main() -> None:
    print('Loading raw CSV file...')
    raw_df = load_csv(RAW_DATA_PATH)

    print('Cleaning dataset...')
    clean_df = clean_data(RAW_DATA_PATH, CLEAN_DATA_PATH)

    print('Writing summary report...')
    run_analysis(raw_df, clean_df, REPORT_PATH)

    print('Generating plots...')
    generate_plots(clean_df, OUTPUT_DIR)

    print('Pipeline finished successfully.')
    print(f'Processed CSV: {CLEAN_DATA_PATH}')
    print(f'Report:        {REPORT_PATH}')
    print(f'Plots:         {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
