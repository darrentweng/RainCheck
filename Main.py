import streamlit as st
import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

mongo_secrets = st.secrets.mongo

uri = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['cluster_url']}/weatherDB?retryWrites=true&w=majority&appName=WeatherApp"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

# Access the database and collection
db = client.weatherDB
collection = db.weatherData

# Test
try:
    client.admin.command("ping")
    st.toast("Connected to database successfully!")
except Exception as e:
    st.error(f"Could not connect to MongoDB: {e}")


def load_data(file_path):
    df = pd.read_csv(file_path)
    df["DATE"] = pd.to_datetime(df["DATE"], format="%m/%d/%Y")
    df.set_index(["NAME", "DATE"], inplace=True)
    return df


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
            (all_years_ma.index.month == date.month)
            & (all_years_ma.index.day >= date.day - days_range)
            & (all_years_ma.index.day <= date.day + days_range)
        )
        relevant_data = all_years_ma[mask]

        if field in ["TMAX", "AWND"]:
            prob = (relevant_data > threshold).mean()
        elif field in ["PRCP", "SNOW"]:
            prob = (relevant_data >= threshold).mean()
        elif field in ["TMIN"]:
            prob = (relevant_data < threshold).mean()

        probabilities[date] = prob

    return probabilities


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


st.title("Weather Insurance Calculator")
