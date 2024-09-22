import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from Main import load_data, weather_probability


# Load data
@st.cache_data
def load_weather_data():
    return load_data("weather.csv")


data = load_weather_data()

st.subheader("Weather Insurance Quotes")

# Input parameters
col1, col2, col3 = st.columns(3)
with col1:
    name = st.selectbox(
        "Select Location", options=data.index.get_level_values("NAME").unique(), index=1
    )
with col2:
    ma_type = st.selectbox(
        "Moving Average", options=["None", "SMA", "WMA", "EMA", "TMA"], index=0
    )
with col3:
    window = st.number_input("Smoothing Window", value=3)


with col1:
    start_date = st.date_input("Start Date", datetime.now() + timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", datetime.now() + timedelta(days=40))
with col3:
    days_range = st.number_input("Date Range (Averaging Window)", value=7)

insurance_amount = st.number_input("Daily Insurance Amount ($)", value=1000, step=100)


with col1:
    temp_max = st.number_input("Maximum Temperature Threshold (°F)", value=90)
with col2:
    temp_min = st.number_input("Minimum Temperature Threshold (°F)", value=40)
with col3:
    prcp = st.number_input("Precipitation Threshold (inches)", value=1.0, step=0.1)


def calculate_premium(probability, insurance_amount):
    return probability * insurance_amount


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


if st.button("Calculate Premiums"):
    probabilities = weather_probability(
        data,
        name,
        start_date,
        end_date,
        temp_max,
        temp_min,
        prcp,
        days_range,
        ma_type,
        window,
    )

    results = []
    for current_date in date_range(start_date, end_date):
        if all(
            field in probabilities and current_date in probabilities[field]
            for field in ["TMAX", "TMIN", "PRCP"]
        ):
            prob = 1.0 - (
                (1.0 - probabilities["TMAX"][current_date])
                * (1.0 - probabilities["TMIN"][current_date])
                * (1.0 - probabilities["PRCP"][current_date])
            )
            premium = calculate_premium(prob, insurance_amount)
            results.append(
                {
                    "Date": current_date.strftime("%m/%d"),
                    "Max Temp Prob": f"{probabilities['TMAX'][current_date]:.2%}",
                    "Min Temp Prob": f"{probabilities['TMIN'][current_date]:.2%}",
                    "Precip Prob": f"{probabilities['PRCP'][current_date]:.2%}",
                    "Premium": f"${premium:.2f}",
                }
            )

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)

        total_premium = sum(float(row["Premium"][1:]) for row in results)
        st.write(f"Total premium for the selected period: ${total_premium:.2f}")
    else:
        st.error("No data available for the selected parameters.")

# Display data range
station_data = data.loc[name]
min_date = station_data.index.min().date()
max_date = station_data.index.max().date()
st.info(
    f"Data available for {name} from {min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')}"
)
