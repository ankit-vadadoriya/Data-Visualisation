from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "[5442] EcoMoveMobility.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    data = pd.read_excel(DATA_FILE, engine="openpyxl")
    return data.drop_duplicates(subset="Record_ID").copy()


def run(data=None):
    df = load_data() if data is None else data.copy()
    city = (
        df.groupby("City", as_index=False)["Passengers"]
        .sum()
        .sort_values("Passengers", ascending=True)
    )

    print("\nPassenger demand by city")
    print(city.sort_values("Passengers", ascending=False).to_string(index=False))

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(city["City"], city["Passengers"])
    ax.set_title("Passenger Demand by City")
    ax.set_xlabel("Passengers")
    ax.set_ylabel("City")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000_000:.1f}M"))
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()

    output = OUTPUT_DIR / "02_city_passenger_demand.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    run()
