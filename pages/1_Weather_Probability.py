import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from Main import load_data, weather_probability


# Load data
@st.cache_data
def load_weather_data():
    return load_data()


data = load_weather_data()

# Streamlit UI
st.subheader("Weather Probability")

# Input parameters
name = st.selectbox(
    "Select Location", options=data.index.get_level_values("NAME").unique()
)

# Create a date input without year
months = list(range(1, 13))
days = list(range(1, 32))

col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("Select A Date", datetime.now() + timedelta(days=30))
with col2:
    days_range = st.number_input("Date Range", value=7)

col1, col2, col3 = st.columns(3)
with col1:
    temp_max = st.number_input("Maximum Temperature Threshold (°F)", value=90)
with col2:
    temp_min = st.number_input("Minimum Temperature Threshold (°F)", value=32)
with col3:
    prcp = st.number_input("Precipitation Threshold (inches)", value=0.5, step=0.1)

if st.button("Calculate Probabilities"):
    result = weather_probability(
        data, name, selected_date, selected_date, temp_max, temp_min, prcp, days_range
    )
    if all(prob is not None for prob in result.values()):
        for field, probabilities in result.items():
            prob = list(probabilities.values())[
                0
            ]  # Get the probability for the selected date
            if field == "TMAX":
                st.write(
                    f"Probability of maximum temperature being higher than {temp_max}°F: {prob:.2%}"
                )
            elif field == "TMIN":
                st.write(
                    f"Probability of minimum temperature being lower than {temp_min}°F: {prob:.2%}"
                )
            elif field == "PRCP":
                st.write(
                    f"Probability of precipitation being higher than {prcp} inches: {prob:.2%}"
                )
    else:
        st.error(
            "Not enough data to calculate probabilities for the selected parameters."
        )

# Display data range
station_data = data.loc[name]
min_date = station_data.index.min().date()
max_date = station_data.index.max().date()
st.info(
    f"Data available for {name} from {min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')}"
)
