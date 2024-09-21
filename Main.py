import streamlit as st
import csv
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

mongo_secrets = st.secrets.mongo

uri = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['cluster_url']}/weatherDB?retryWrites=true&w=majority&appName=WeatherApp"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Access the database and collection
db = client.weatherDB
collection = db.weatherData

def get_weather_data():
    data = {}
    cursor = collection.find({})
    for document in cursor:
        name = document['name']
        date = document['date']
        if name not in data:
            data[name] = {}
        data[name][date] = document
    return data

def get_probability(data, name, target_month, target_day, days_range, field, threshold):
    relevant_data = []
    for date in data[name]:
        if date.month == target_month and date.day == target_day:
            start_date = date - timedelta(days=days_range)
            end_date = date + timedelta(days=days_range)
            for other_date in data[name]:
                if start_date <= other_date <= end_date and data[name][other_date][field] is not None:
                    relevant_data.append(float(data[name][other_date][field]))
    
    if not relevant_data:
        return None
    
    if field in ['tmax', 'tmin', 'prcp']:
        higher_count = sum(1 for value in relevant_data if value > threshold)
        return higher_count / len(relevant_data)
    
    return None

def weather_probability(data, name, month, day, temp_max, temp_min, prcp, range_days):
    tmax_prob = get_probability(data, name, month, day, range_days, 'tmax', temp_max)
    tmin_prob = get_probability(data, name, month, day, range_days, 'tmin', temp_min)
    prcp_prob = get_probability(data, name, month, day, range_days, 'prcp', prcp)
    
    return {
        'TMAX': tmax_prob,
        'TMIN': tmin_prob,
        'PRCP': prcp_prob
    }

# Optional: Test the connection
try:
    client.admin.command('ping')
    st.write("Connected to MongoDB successfully!")
except Exception as e:
    st.error(f"Could not connect to MongoDB: {e}")
