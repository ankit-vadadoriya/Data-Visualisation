from pathlib import Path

import matplotlib.pyplot as plt
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
    mode = (
        df.groupby("Transport_Mode", as_index=False)
        .agg(
            Passengers=("Passengers", "sum"),
            Complaints=("Accessibility_Complaints", "sum"),
            CO2=("CO2_Saved_KG", "sum"),
            Energy=("Energy_Consumption_KWh", "sum"),
        )
    )
    mode["Complaints_per_10k"] = mode["Complaints"] / mode["Passengers"] * 10_000
    mode["CO2_per_1000"] = mode["CO2"] / mode["Passengers"] * 1_000
    mode["Energy_per_1000"] = mode["Energy"] / mode["Passengers"] * 1_000

    print("\nAccessibility and sustainability by transport mode")
    print(
        mode[
            ["Transport_Mode", "Passengers", "Complaints_per_10k", "CO2_per_1000", "Energy_per_1000"]
        ].round(2).to_string(index=False)
    )

    bubble_size = 180 + (mode["Passengers"] / mode["Passengers"].max()) * 1400
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.scatter(
        mode["Complaints_per_10k"],
        mode["CO2_per_1000"],
        s=bubble_size,
        alpha=0.6,
        edgecolors="black",
        linewidths=0.7,
    )

    for _, row in mode.iterrows():
        ax.annotate(
            row["Transport_Mode"],
            (row["Complaints_per_10k"], row["CO2_per_1000"]),
            xytext=(6, 5),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_title("Accessibility and Sustainability by Transport Mode")
    ax.text(
        0.02,
        0.02,
        "Bubble size = passenger demand",
        transform=ax.transAxes,
        fontsize=9,
        va="bottom",
    )
    ax.set_xlabel("Complaints per 10,000 passengers")
    ax.set_ylabel("CO2 saved (kg per 1,000 passengers)")
    ax.grid(alpha=0.2)
    fig.tight_layout()

    output = OUTPUT_DIR / "06_mode_accessibility_sustainability.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    run()
