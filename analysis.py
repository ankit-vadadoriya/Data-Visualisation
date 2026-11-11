from pathlib import Path

import pandas as pd

from visual_01_time_trend import run as run_01
from visual_02_city_demand import run as run_02
from visual_03_delay_distribution import run as run_03
from visual_04_correlation import run as run_04
from visual_05_financial_performance import run as run_05
from visual_06_accessibility_sustainability import run as run_06

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "[5442] EcoMoveMobility.xlsx"

REQUIRED_COLUMNS = {
    "Record_ID",
    "Date",
    "City",
    "Country",
    "Transport_Mode",
    "Route_Type",
    "Weather",
    "Event_Day",
    "Passengers",
    "Trips",
    "Average_Delay_Minutes",
    "On_Time_Percentage",
    "Ticket_Revenue_EUR",
    "Operating_Cost_EUR",
    "CO2_Saved_KG",
    "Energy_Consumption_KWh",
    "Customer_Rating",
    "Accessibility_Complaints",
}


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE.name}")

    data = pd.read_excel(DATA_FILE, engine="openpyxl")
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    original_rows = len(data)
    missing_values = int(data.isna().sum().sum())
    duplicate_ids = int(data["Record_ID"].duplicated().sum())

    if pd.api.types.is_numeric_dtype(data["Date"]):
        converted = pd.to_datetime(data["Date"], unit="D", origin="1899-12-30", errors="coerce")
    else:
        converted = pd.to_datetime(data["Date"], errors="coerce")

    invalid_dates = int(converted.isna().sum())
    data["Date"] = converted
    data = data.drop_duplicates(subset="Record_ID").dropna(subset=["Date"]).copy()

    checks = {
        "rows": original_rows,
        "columns": len(data.columns),
        "missing_values": missing_values,
        "duplicate_ids": duplicate_ids,
        "invalid_dates": invalid_dates,
    }
    return data, checks


def main():
    df, checks = load_data()

    print("Data check")
    print(f"Rows: {checks['rows']:,}")
    print(f"Columns: {checks['columns']}")
    print(f"Date range: {df['Date'].min():%d %b %Y} to {df['Date'].max():%d %b %Y}")
    print(f"Missing values: {checks['missing_values']:,}")
    print(f"Duplicate IDs: {checks['duplicate_ids']:,}")
    print(f"Invalid dates: {checks['invalid_dates']:,}")

    outputs = [
        run_01(df),
        run_02(df),
        run_03(df),
        run_04(df),
        run_05(df),
        run_06(df),
    ]

    print("\nSaved figures")
    for output in outputs:
        print(output.name)


if __name__ == "__main__":
    main()
