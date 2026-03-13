# Smart Sensor Project

A clean and reproducible Python project for loading, cleaning, analyzing, and visualizing Raspberry Pi sensor data from CSV files.

## What this project does

- loads raw sensor data from `data/raw/sensors.csv`
- cleans timestamps and numeric values
- removes invalid or unrealistic sensor readings
- computes engineered features such as temperature difference and hour of day
- writes a cleaned dataset to `data/processed/sensors_clean.csv`
- generates a text report in `data/reports/summary.txt`
- creates organized plots in `outputs/`

## Expected CSV columns

The raw dataset should contain these columns:

- `timestamp`
- `lux`
- `bmp_temp_c`
- `bmp_press_hpa`
- `dht_temp_c`
- `dht_hum_pct`

## Project structure

```text
smart_sensor/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   │   └── sensors.csv
│   ├── processed/
│   │   └── sensors_clean.csv
│   └── reports/
│       └── summary.txt
├── outputs/
│   └── *.png
└── src/
    ├── load.py
    ├── clean.py
    ├── analyze.py
    ├── plots.py
    ├── advanced_analysis.py
    └── main.py
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the full pipeline

From the project root:

```bash
python src/main.py
```

## Output files

After running the pipeline you should get:

- cleaned data in `data/processed/`
- a summary report in `data/reports/`
- PNG plots in `outputs/`

## Notes

- The repository is prepared to be uploaded to GitHub.
- Virtual environments, cache folders, and PDF reports should stay out of version control.
- Plotting was adjusted to improve date formatting, readability, and outlier handling.
