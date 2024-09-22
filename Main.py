import streamlit as st
import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from io import StringIO
import datetime

# MongoDB Connection Setup
mongo_secrets = st.secrets.mongo

uri = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['cluster_url']}/weatherDB?retryWrites=true&w=majority&appName=WeatherApp"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

# Access the database and collection
db = client.weatherDB
collection = db.weatherData

# Test Connection
try:
    client.admin.command("ping")
    st.success("Connected to MongoDB successfully!")
except Exception as e:
    st.error(f"Could not connect to MongoDB: {e}")
    st.stop()  # Stop the app if the database connection fails

# Function to Upload CSV Data to MongoDB
def upload_csv_to_mongodb(uploaded_file):
    try:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        
        # Ensure DATE column is in datetime format
        df["DATE"] = pd.to_datetime(df["DATE"], format="%m/%d/%Y")
        
        # Convert DataFrame to dictionary records
        records = df.to_dict(orient='records')
        
        # Optional: Clear existing data to prevent duplicates
        # Uncomment the next line if you want to clear existing data before upload
        # collection.delete_many({})
        
        # Insert records into MongoDB
        if records:
            collection.insert_many(records)
            st.success("CSV data uploaded to MongoDB successfully!")
        else:
            st.warning("No records found in the uploaded CSV.")
    except Exception as e:
        st.error(f"Error uploading CSV to MongoDB: {e}")

# Function to Load Data from MongoDB
@st.cache_data  # Cache the data to improve performance
def load_data():
    try:
        # Query all documents in the collection
        cursor = collection.find({})
        data = list(cursor)
        
        if not data:
            st.warning("No data found in MongoDB. Please upload a CSV file first.")
            return pd.DataFrame()  # Return empty DataFrame
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(data)
        
        # Convert DATE column to datetime if not already
        if not np.issubdtype(df['DATE'].dtype, np.datetime64):
            df["DATE"] = pd.to_datetime(df["DATE"], format="%m/%d/%Y")
        
        # Set multi-index
        df.set_index(["NAME", "DATE"], inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data from MongoDB: {e}")
        return pd.DataFrame()

# Function to Calculate Moving Average 
def calculate_moving_average(data, window, ma_type):

    if ma_type == "SMA":
        return data.rolling(window=window).mean()
    elif ma_type == "WMA":
        weights = np.arange(1, window + 1)
        return data.rolling(window=window).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
    elif ma_type == "EMA":
        return data.ewm(span=window, adjust=False).mean()
    elif ma_type == "TMA":
        sma = data.rolling(window=window).mean()
        return sma.rolling(window=window).mean()
    else:
        return data

# Function to Get Probabilities
def get_probabilities(
    data,
    name,
    start_date,
    end_date,
    days_range,
    field,
    threshold,
    ma_type=None,
    window=5,
):
    print(f"Getting probabilities for {field}")
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Separate smoothing for each year
    results = []
    for year in data.index.get_level_values("DATE").year.unique():
        year_data = data[data.index.get_level_values("DATE").year == year]

        # Expand the date range for each year
        expanded_dates = pd.date_range(
            start=year_data.index.get_level_values("DATE").min()
            - pd.Timedelta(days=window),
            end=year_data.index.get_level_values("DATE").max()
            + pd.Timedelta(days=window),
            freq="D",
        )

        # Reindex the data with the expanded date range
        year_data = year_data.reindex(expanded_dates, level="DATE")

        # Apply the mask for the specific date range
        mask = (
            (year_data.index.get_level_values("NAME") == name)
            & (
                year_data.index.get_level_values("DATE")
                >= start_date.replace(year=year)
            )
            & (year_data.index.get_level_values("DATE") <= end_date.replace(year=year))
        )
        relevant_data = year_data.loc[mask, field].dropna()

        # Calculate moving average for the year
        ma_data = calculate_moving_average(
            relevant_data, window=window, ma_type=ma_type
        )
        results.append(ma_data)

    # Concatenate results from all years
    all_years_ma = pd.concat(results)

    if all_years_ma.empty:
        return None

    # Calculate probabilities for each date in the range
    date_range = pd.date_range(start=start_date, end=end_date)
    probabilities = {}
    for date in date_range:
        mask = (
            (all_years_ma.index.get_level_values("DATE").month == date.month)
            & (all_years_ma.index.get_level_values("DATE").day >= date.day - days_range)
            & (all_years_ma.index.get_level_values("DATE").day <= date.day + days_range)
        )
        relevant_data = all_years_ma[mask]

        if relevant_data.empty:
            prob = None  # Handle cases with no relevant data
        elif field in ["TMAX", "AWND"]:
            prob = (relevant_data > threshold).mean()
        elif field in ["PRCP", "SNOW"]:
            prob = (relevant_data >= threshold).mean()
        elif field in ["TMIN"]:
            prob = (relevant_data < threshold).mean()
        else:
            prob = None  # Handle unexpected fields

        probabilities[date] = prob

    return probabilities


# Function to Calculate Weather Probability
def weather_probability(
    data,
    name,
    start_date,
    end_date,
    temp_max,
    temp_min,
    prcp,
    range,
    ma_type=None,
    window=5,
):
    return {
        "TMAX": get_probabilities(
            data, name, start_date, end_date, range, "TMAX", temp_max, ma_type, window
        ),
        "TMIN": get_probabilities(
            data, name, start_date, end_date, range, "TMIN", temp_min, ma_type, window
        ),
        "PRCP": get_probabilities(
            data, name, start_date, end_date, range, "PRCP", prcp, ma_type, window
        ),
    }

# Streamlit App Layout
st.title("Weather Insurance Calculator")

# Section to Upload CSV to MongoDB
st.header("Upload Weather Data CSV to MongoDB")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    if st.button("Upload CSV to Database"):
        upload_csv_to_mongodb(uploaded_file)

# Load Data from MongoDB
data = load_data()


# Optional: Display Data from MongoDB
if st.checkbox("Show Raw Data from MongoDB"):
    st.subheader("Raw Weather Data")
    st.dataframe(data.reset_index())
