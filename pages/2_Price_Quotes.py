import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from Main import get_weather_data, get_probability, weather_probability

# Load data
@st.cache_data
def load_weather_data():
    return get_weather_data()

data = load_weather_data()

st.title('Weather Insurance Quotes')

# Input parameters
col1, col2 = st.columns(2)
with col1:
    name = st.selectbox('Select Location', options=list(data.keys()), index=1)
with col2:
    days_range = st.number_input('Date Range', value=7)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input('Start Date', datetime.now()+ timedelta(days=30))
with col2:
    end_date = st.date_input('End Date', datetime.now()+ timedelta(days=40))

insurance_amount = st.number_input('Daily Insurance Amount ($)', value=1000, step=100)

col1, col2, col3 = st.columns(3)
with col1:
    temp_max = st.number_input('Maximum Temperature Threshold (°F)', value=90)
with col2:
    temp_min = st.number_input('Minimum Temperature Threshold (°F)', value=32)
with col3:
    prcp = st.number_input('Precipitation Threshold (inches)', value=1.0, step=0.1)

def calculate_premium(probability, insurance_amount):
    return probability * insurance_amount

def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

if st.button('Calculate Premiums'):
    results = []
    for current_date in date_range(start_date, end_date):
        month, day = current_date.month, current_date.day
        
        probabilities = weather_probability(data, name, month, day, temp_max, temp_min, prcp, days_range)
        
        if all(prob is not None for prob in probabilities.values()):
            prob = 1.0 - ((1.0 - probabilities['TMAX'])*(probabilities['TMIN'])*(1.0 - probabilities['PRCP']))
            premium = calculate_premium(prob, insurance_amount)
            results.append({
                'Date': f"{month}/{day}",
                'Max Temp Prob': f"{probabilities['TMAX']:.2%}",
                'Min Temp Prob': f"{1-probabilities['TMIN']:.2%}",
                'Precip Prob': f"{probabilities['PRCP']:.2%}",
                'Premium': f'${premium:.2f}'
            })
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        total_premium = sum(float(row['Premium'][1:]) for row in results)
        st.write(f"Total premium for the selected period: ${total_premium:.2f}")
    else:
        st.error("No data available for the selected parameters.")

# Display data range
if name in data:
    min_date = min(data[name].keys())
    max_date = max(data[name].keys())
    st.info(f"Data available for {name} from {min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')}")