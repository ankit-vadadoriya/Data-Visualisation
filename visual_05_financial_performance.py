from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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
    finance = (
        df.groupby("Transport_Mode", as_index=False)
        .agg(
            Revenue=("Ticket_Revenue_EUR", "sum"),
            Cost=("Operating_Cost_EUR", "sum"),
        )
        .sort_values("Revenue", ascending=False)
    )
    finance["Balance"] = finance["Revenue"] - finance["Cost"]

    print("\nFinancial performance by transport mode")
    print(finance.round(2).to_string(index=False))

    x = np.arange(len(finance))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, finance["Revenue"] / 1_000_000, width, label="Revenue")
    ax.bar(x + width / 2, finance["Cost"] / 1_000_000, width, label="Cost")
    ax.set_xticks(x)
    ax.set_xticklabels(finance["Transport_Mode"], rotation=25, ha="right")
    ax.set_title("Revenue and Cost by Transport Mode")
    ax.set_xlabel("Transport mode")
    ax.set_ylabel("EUR (millions)")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()

    output = OUTPUT_DIR / "05_mode_revenue_cost.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    run()
