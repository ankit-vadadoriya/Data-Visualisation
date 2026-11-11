from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

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


@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE.name}")

    data = pd.read_excel(DATA_FILE, engine="openpyxl")
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    if pd.api.types.is_numeric_dtype(data["Date"]):
        data["Date"] = pd.to_datetime(data["Date"], unit="D", origin="1899-12-30", errors="coerce")
    else:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    return data.drop_duplicates(subset="Record_ID").dropna(subset=["Date"]).copy()


def apply_filter(data, column, values):
    if values:
        return data[data[column].isin(values)]
    return data


def weighted_mean(data, value, weight):
    valid = data[[value, weight]].dropna()
    if valid.empty or valid[weight].sum() == 0:
        return np.nan
    return np.average(valid[value], weights=valid[weight])


def weighted_group(data, group, value, weight, result_name):
    temp = data[[group, value, weight]].dropna().copy()
    temp["weighted"] = temp[value] * temp[weight]
    grouped = temp.groupby(group, as_index=False).agg(
        weighted_sum=("weighted", "sum"),
        weight_sum=(weight, "sum"),
    )
    grouped[result_name] = grouped["weighted_sum"] / grouped["weight_sum"]
    return grouped[[group, result_name]]


def clean_figure(fig):
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="",
    )
    return fig


st.set_page_config(page_title="EcoMove Mobility Dashboard", layout="wide")
st.title("EcoMove Mobility Dashboard")
st.caption("Demand, reliability, financial, accessibility and sustainability performance")

try:
    df = load_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.sidebar.header("Filters")

start_date = df["Date"].min().date()
end_date = df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(start_date, end_date),
    min_value=start_date,
    max_value=end_date,
)

countries = st.sidebar.multiselect("Country", sorted(df["Country"].unique()))
city_source = df[df["Country"].isin(countries)] if countries else df
cities = st.sidebar.multiselect("City", sorted(city_source["City"].unique()))
modes = st.sidebar.multiselect("Transport mode", sorted(df["Transport_Mode"].unique()))
routes = st.sidebar.multiselect("Route type", sorted(df["Route_Type"].unique()))
weather = st.sidebar.multiselect("Weather", sorted(df["Weather"].unique()))
events = st.sidebar.multiselect("Event day", sorted(df["Event_Day"].unique()))

filtered = df.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"].dt.date >= date_range[0])
        & (filtered["Date"].dt.date <= date_range[1])
    ]
filtered = apply_filter(filtered, "Country", countries)
filtered = apply_filter(filtered, "City", cities)
filtered = apply_filter(filtered, "Transport_Mode", modes)
filtered = apply_filter(filtered, "Route_Type", routes)
filtered = apply_filter(filtered, "Weather", weather)
filtered = apply_filter(filtered, "Event_Day", events)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

revenue = filtered["Ticket_Revenue_EUR"].sum()
cost = filtered["Operating_Cost_EUR"].sum()
balance = revenue - cost
avg_delay = weighted_mean(filtered, "Average_Delay_Minutes", "Trips")
on_time = weighted_mean(filtered, "On_Time_Percentage", "Trips")
rating = weighted_mean(filtered, "Customer_Rating", "Passengers")

row1 = st.columns(4)
row1[0].metric("Passengers", f"{filtered['Passengers'].sum():,.0f}")
row1[1].metric("Trips", f"{filtered['Trips'].sum():,.0f}")
row1[2].metric("Avg delay", f"{avg_delay:.1f} min")
row1[3].metric("On time", f"{on_time:.1f}%")

row2 = st.columns(4)
row2[0].metric("Revenue", f"€{revenue / 1_000_000:.2f}M")
row2[1].metric("Cost", f"€{cost / 1_000_000:.2f}M")
row2[2].metric("Balance", f"€{balance / 1_000_000:.2f}M")
row2[3].metric("Rating", f"{rating:.2f}")

row3 = st.columns(3)
row3[0].metric("CO2 saved", f"{filtered['CO2_Saved_KG'].sum() / 1_000:.1f} t")
row3[1].metric("Energy", f"{filtered['Energy_Consumption_KWh'].sum() / 1_000:.1f} MWh")
row3[2].metric("Complaints", f"{filtered['Accessibility_Complaints'].sum():,.0f}")

overview_tab, reliability_tab, finance_tab, sustainability_tab = st.tabs(
    ["Overview", "Reliability", "Finance", "Sustainability"]
)

with overview_tab:
    monthly = (
        filtered.assign(Month=filtered["Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)["Passengers"]
        .sum()
    )
    fig = px.line(monthly, x="Month", y="Passengers", markers=True, title="Monthly Passenger Demand")
    fig.update_xaxes(range=[monthly["Month"].min(), monthly["Month"].max()])
    fig.update_yaxes(tickformat="~s")
    st.plotly_chart(clean_figure(fig), use_container_width=True)

    left, right = st.columns(2)
    country = filtered.groupby("Country", as_index=False)["Passengers"].sum().sort_values("Passengers")
    fig = px.bar(country, x="Passengers", y="Country", orientation="h", title="Passenger Demand by Country")
    fig.update_xaxes(tickformat="~s")
    left.plotly_chart(clean_figure(fig), use_container_width=True)

    city = filtered.groupby("City", as_index=False)["Passengers"].sum().sort_values("Passengers")
    fig = px.bar(city, x="Passengers", y="City", orientation="h", title="Passenger Demand by City")
    fig.update_xaxes(tickformat="~s")
    right.plotly_chart(clean_figure(fig), use_container_width=True)

    route = filtered.groupby("Route_Type", as_index=False)["Passengers"].sum().sort_values("Passengers")
    fig = px.bar(
        route,
        x="Passengers",
        y="Route_Type",
        orientation="h",
        title="Passenger Demand by Route Type",
        labels={"Route_Type": "Route type"},
    )
    fig.update_xaxes(tickformat="~s")
    st.plotly_chart(clean_figure(fig), use_container_width=True)

with reliability_tab:
    left, right = st.columns(2)

    mode_delay = weighted_group(
        filtered,
        "Transport_Mode",
        "Average_Delay_Minutes",
        "Trips",
        "Avg_Delay",
    ).sort_values("Avg_Delay")
    fig = px.bar(
        mode_delay,
        x="Avg_Delay",
        y="Transport_Mode",
        orientation="h",
        title="Average Delay by Transport Mode",
        labels={"Avg_Delay": "Delay minutes", "Transport_Mode": "Transport mode"},
    )
    fig.update_xaxes(tickformat=".1f")
    left.plotly_chart(clean_figure(fig), use_container_width=True)

    weather_delay = weighted_group(
        filtered,
        "Weather",
        "Average_Delay_Minutes",
        "Trips",
        "Avg_Delay",
    ).sort_values("Avg_Delay")
    fig = px.bar(
        weather_delay,
        x="Avg_Delay",
        y="Weather",
        orientation="h",
        title="Average Delay by Weather",
        labels={"Avg_Delay": "Delay minutes"},
    )
    fig.update_xaxes(tickformat=".1f")
    right.plotly_chart(clean_figure(fig), use_container_width=True)

    left, right = st.columns(2)
    route_on_time = weighted_group(
        filtered,
        "Route_Type",
        "On_Time_Percentage",
        "Trips",
        "On_Time",
    ).sort_values("On_Time")
    fig = px.bar(
        route_on_time,
        x="On_Time",
        y="Route_Type",
        orientation="h",
        title="On-Time Performance by Route Type",
        labels={"On_Time": "On time %", "Route_Type": "Route type"},
    )
    fig.update_xaxes(tickformat=".1f", ticksuffix="%")
    left.plotly_chart(clean_figure(fig), use_container_width=True)

    mode_rating = weighted_group(
        filtered,
        "Transport_Mode",
        "Customer_Rating",
        "Passengers",
        "Rating",
    ).sort_values("Rating")
    fig = px.bar(
        mode_rating,
        x="Rating",
        y="Transport_Mode",
        orientation="h",
        title="Customer Rating by Transport Mode",
        labels={"Transport_Mode": "Transport mode"},
    )
    fig.update_xaxes(tickformat=".2f")
    right.plotly_chart(clean_figure(fig), use_container_width=True)

with finance_tab:
    finance = (
        filtered.groupby("Transport_Mode", as_index=False)
        .agg(Revenue=("Ticket_Revenue_EUR", "sum"), Cost=("Operating_Cost_EUR", "sum"))
    )
    finance["Balance"] = finance["Revenue"] - finance["Cost"]
    finance_long = finance.melt(
        id_vars="Transport_Mode",
        value_vars=["Revenue", "Cost"],
        var_name="Measure",
        value_name="EUR",
    )
    fig = px.bar(
        finance_long,
        x="Transport_Mode",
        y="EUR",
        color="Measure",
        barmode="group",
        title="Revenue and Cost by Transport Mode",
        labels={"Transport_Mode": "Transport mode"},
    )
    fig.update_yaxes(tickformat="~s", tickprefix="€")
    st.plotly_chart(clean_figure(fig), use_container_width=True)

    fig = px.bar(
        finance.sort_values("Balance"),
        x="Balance",
        y="Transport_Mode",
        orientation="h",
        title="Operating Balance by Transport Mode",
        labels={"Transport_Mode": "Transport mode"},
    )
    fig.update_xaxes(tickformat="~s", tickprefix="€")
    st.plotly_chart(clean_figure(fig), use_container_width=True)

with sustainability_tab:
    mode = (
        filtered.groupby("Transport_Mode", as_index=False)
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

    left, right = st.columns(2)
    fig = px.bar(
        mode.sort_values("Complaints_per_10k"),
        x="Complaints_per_10k",
        y="Transport_Mode",
        orientation="h",
        title="Accessibility Complaint Rate",
        labels={"Complaints_per_10k": "Complaints per 10,000 passengers", "Transport_Mode": "Transport mode"},
    )
    fig.update_xaxes(tickformat=".1f")
    left.plotly_chart(clean_figure(fig), use_container_width=True)

    fig = px.bar(
        mode.sort_values("CO2_per_1000"),
        x="CO2_per_1000",
        y="Transport_Mode",
        orientation="h",
        title="CO2 Saved per 1,000 Passengers",
        labels={"CO2_per_1000": "CO2 saved (kg per 1,000 passengers)", "Transport_Mode": "Transport mode"},
    )
    fig.update_xaxes(tickformat=".1f")
    right.plotly_chart(clean_figure(fig), use_container_width=True)

    fig = px.bar(
        mode.sort_values("Energy_per_1000"),
        x="Energy_per_1000",
        y="Transport_Mode",
        orientation="h",
        title="Energy Use per 1,000 Passengers",
        labels={"Energy_per_1000": "Energy (kWh per 1,000 passengers)", "Transport_Mode": "Transport mode"},
    )
    fig.update_xaxes(tickformat=".1f")
    st.plotly_chart(clean_figure(fig), use_container_width=True)

st.caption(f"Showing {len(filtered):,} of {len(df):,} records")
