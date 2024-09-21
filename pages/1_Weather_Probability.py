import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from Main import get_weather_data, get_probability, weather_probability
# Load data
@st.cache_data
def load_weather_data():
    return get_weather_data()

data = load_weather_data()

# Streamlit UI
st.title('Weather Probability')

# Input parameters
name = st.selectbox('Select Location', options=list(data.keys()))

# Create a date input without year
months = list(range(1, 13))
days = list(range(1, 32))

col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input('Select A Date', datetime.now()+ timedelta(days=30))
with col2:
    days_range = st.number_input('Date Range', value=7)

col1, col2, col3 = st.columns(3)
with col1:
    temp_max = st.number_input('Maximum Temperature Threshold (°F)', value=90)
with col2:
    temp_min = st.number_input('Minimum Temperature Threshold (°F)', value=32)
with col3:
    prcp = st.number_input('Precipitation Threshold (inches)', value=0.5, step=0.1)

if st.button('Calculate Probabilities'):
    month, day = selected_date.month, selected_date.day
    result = weather_probability(data, name, month, day, temp_max, temp_min, prcp, days_range)
    
    if all(prob is not None for prob in result.values()):
        st.write(f"Probability of maximum temperature being higher than {temp_max}°F: {result['TMAX']:.2%}")
        st.write(f"Probability of minimum temperature being lower than {temp_min}°F: {1 - result['TMIN']:.2%}")
        st.write(f"Probability of precipitation being higher than {prcp} inches: {result['PRCP']:.2%}")
    else:
        st.error("Not enough data to calculate probabilities for the selected parameters.")

# Display data range
if name in data:
    min_date = min(data[name].keys())
    max_date = max(data[name].keys())
    st.info(f"Data available for {name} from {min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')}")