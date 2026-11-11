from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "[5442] EcoMoveMobility.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    data = pd.read_excel(DATA_FILE, engine="openpyxl")
    return data.drop_duplicates(subset="Record_ID").copy()


def run(data=None):
    df = load_data() if data is None else data.copy()
    weather_order = ["Clear", "Cloudy", "Rain", "Windy", "Heatwave", "Snow"]
    event_order = ["No", "Yes"]
    colors = {"No": "#4C78A8", "Yes": "#F58518"}
    hatches = {"No": "", "Yes": "//"}

    summary = (
        df.groupby(["Weather", "Event_Day"], as_index=False)
        .agg(
            Avg_Delay=("Average_Delay_Minutes", "mean"),
            Median_Delay=("Average_Delay_Minutes", "median"),
        )
    )
    print("\nDelay by weather and event day")
    print(summary.round(2).to_string(index=False))

    positions = np.arange(len(weather_order))
    width = 0.32
    fig, ax = plt.subplots(figsize=(11, 6))

    for event in event_order:
        box_data = [
            df.loc[
                (df["Weather"] == weather) & (df["Event_Day"] == event),
                "Average_Delay_Minutes",
            ].dropna().values
            for weather in weather_order
        ]
        offset = -width / 2 if event == "No" else width / 2
        box = ax.boxplot(
            box_data,
            positions=positions + offset,
            widths=width * 0.85,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "black", "linewidth": 1.4},
            whiskerprops={"color": "#444444", "linewidth": 1.0},
            capprops={"color": "#444444", "linewidth": 1.0},
        )

        for patch in box["boxes"]:
            patch.set_facecolor(colors[event])
            patch.set_edgecolor("#444444")
            patch.set_alpha(0.72)
            patch.set_hatch(hatches[event])

    ax.set_xticks(positions)
    ax.set_xticklabels(weather_order)
    ax.set_title("Delay Distribution by Weather and Event Day")
    ax.set_xlabel("Weather")
    ax.set_ylabel("Delay (minutes)")
    ax.legend(
        handles=[
            Patch(facecolor=colors["No"], edgecolor="#444444", label="Normal day", alpha=0.72),
            Patch(facecolor=colors["Yes"], edgecolor="#444444", hatch="//", label="Event day", alpha=0.72),
        ],
        frameon=False,
        loc="upper left",
    )
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()

    output = OUTPUT_DIR / "03_delay_weather_event.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    run()
