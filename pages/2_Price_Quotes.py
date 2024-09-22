import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from Main import load_data, weather_probability
from nessie import get_customer_accounts, get_api_key, delete_data, get_customers, get_merchants, create_account, create_merchant, create_purchase, create_customer


# Load data
@st.cache_data
def load_weather_data():
    return load_data()


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

if 'quotestage' not in st.session_state:
    st.session_state.quotestage = 0

def set_quotestage(i):
    st.session_state.quotestage = i


if st.session_state.quotestage == 0:
    st.button('Calculate Premiums', on_click=set_quotestage, args=[1])


if st.session_state.quotestage >= 1:
    st.write("Calculating probabilities")
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
    print(probabilities)

    if probabilities is None:
        st.error("No data available for the selected parameters.")
    else:
        results = []
        for current_date in date_range(start_date, end_date):
            # Convert current_date to pd.Timestamp to match probabilities keys
            current_timestamp = pd.Timestamp(current_date)

            if all(
                field in probabilities and current_timestamp in probabilities[field]
                for field in ["TMAX", "TMIN", "PRCP"]
            ):
                prob_tmax = probabilities["TMAX"].get(current_timestamp, 0)
                prob_tmin = probabilities["TMIN"].get(current_timestamp, 0)
                prob_prcp = probabilities["PRCP"].get(current_timestamp, 0)

                # Ensure probabilities are valid numbers
                if any(pd.isna([prob_tmax, prob_tmin, prob_prcp])):
                    continue

                prob = 1.0 - (
                    (1.0 - prob_tmax)
                    * (1.0 - prob_tmin)
                    * (1.0 - prob_prcp)
                )
                premium = calculate_premium(prob, insurance_amount)
                results.append(
                    {
                        "Date": current_date.strftime("%m/%d"),
                        "Max Temp Prob": f"{prob_tmax:.2%}",
                        "Min Temp Prob": f"{prob_tmin:.2%}",
                        "Precip Prob": f"{prob_prcp:.2%}",
                        "Premium": f"${premium:.2f}",
                    }
                )

    

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)

        total_premium = sum(float(row["Premium"][1:]) for row in results)
        st.write(f"Total premium for the selected period: ${total_premium:.2f}")
        set_quotestage(2)

    else:
        st.error("No data available for the selected parameters.")

if st.session_state.quotestage >= 2:
    # Call Nessie API to create a purchase
    api_key = get_api_key()

    customers = get_customers(api_key)
    customer_id = customers[0]["_id"]  # Replace with actual customer_id

    accounts = get_customer_accounts(customer_id, api_key)
    account_id = accounts[0]["_id"]   # Replace with actual account_id

    merchants = get_merchants(api_key)
    merchant_id = merchants[0]["_id"]  # Replace with actual merchant_id
    description = "Weather insurance premium payment"
    
    total_premium_markup = total_premium * 1.05
    st.write(f"Total Premium (with markup): ${total_premium_markup:.2f}")
    response = create_purchase(
        account_id=account_id,
        api_key=api_key,
        merchant_id=merchant_id,
        medium="balance",
        purchase_date=str(datetime.now().date()),
        amount=total_premium_markup,
        status="pending",
        description=description
    )
    
    if response.status_code == 201:
        print("Sucesss")
        #st.success("Payment successful!")
    else:
        print("Fail")
        #st.error(f"Payment failed: {response.text}")

# Display data range
station_data = data.loc[name]
min_date = station_data.index.min().date()
max_date = station_data.index.max().date()
st.info(
    f"Data available for {name} from {min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')}"
)
