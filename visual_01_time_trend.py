from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "[5442] EcoMoveMobility.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    data = pd.read_excel(DATA_FILE, engine="openpyxl")
    if pd.api.types.is_numeric_dtype(data["Date"]):
        data["Date"] = pd.to_datetime(
            data["Date"], unit="D", origin="1899-12-30", errors="coerce"
        )
    else:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    return data.drop_duplicates(subset="Record_ID").dropna(subset=["Date"]).copy()


def run(data=None):
    df = load_data() if data is None else data.copy()
    monthly = (
        df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)["Passengers"]
        .sum()
    )

    print("\nMonthly passenger demand")
    print(monthly.to_string(index=False))

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(monthly["Month"], monthly["Passengers"], marker="o", linewidth=1.8)
    ax.set_title("Monthly Passenger Demand")
    ax.set_xlabel("Month")
    ax.set_ylabel("Passengers")
    ax.set_xlim(monthly["Month"].min(), monthly["Month"].max())
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000_000:.1f}M"))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output = OUTPUT_DIR / "01_monthly_passenger_demand.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    run()
