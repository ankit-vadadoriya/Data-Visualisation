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
    columns = [
        "Passengers",
        "Average_Delay_Minutes",
        "On_Time_Percentage",
        "Ticket_Revenue_EUR",
        "Operating_Cost_EUR",
        "CO2_Saved_KG",
        "Customer_Rating",
        "Accessibility_Complaints",
    ]
    labels = [
        "Passengers",
        "Delay",
        "On time",
        "Revenue",
        "Cost",
        "CO2 saved",
        "Rating",
        "Complaints",
    ]
    corr = df[columns].corr()

    print("\nPerformance metric correlations")
    printable = corr.copy()
    printable.index = labels
    printable.columns = labels
    print(printable.round(2).to_string())

    fig, ax = plt.subplots(figsize=(9, 7.5))
    image = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm", aspect="auto")
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Correlation")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Performance Metric Correlations")

    for i in range(len(labels)):
        for j in range(len(labels)):
            value = corr.iloc[i, j]
            text_color = "white" if abs(value) >= 0.55 else "black"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8, color=text_color)

    fig.tight_layout()
    output = OUTPUT_DIR / "04_performance_correlations.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


if __name__ == "__main__":
    run()
