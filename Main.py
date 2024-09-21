import streamlit as st
import csv
from datetime import datetime, timedelta

def load_data(file_path):
    data = {}
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['NAME']
            date = datetime.strptime(row['DATE'], '%m/%d/%Y')
            if name not in data:
                data[name] = {}
            data[name][date] = row
    return data

def get_probability(data, name, target_month, target_day, days_range, field, threshold):
    relevant_data = []
    for year in set(date.year for date in data[name].keys()):
        target_date = datetime(year, target_month, target_day)
        start_date = target_date - timedelta(days=days_range)
        end_date = target_date + timedelta(days=days_range)
        
        relevant_data.extend([
            float(data[name][date][field])
            for date in data[name]
            if start_date <= date <= end_date and data[name][date][field] != ''
        ])
    
    if not relevant_data:
        return None
    
    if field in ['TMAX', 'TMIN']:
        higher_count = sum(1 for value in relevant_data if value > threshold)
        return higher_count / len(relevant_data)
    elif field == 'PRCP':
        higher_count = sum(1 for value in relevant_data if value > threshold)
        return higher_count / len(relevant_data)

def weather_probability(data, name, month, day, temp_max, temp_min, prcp, range):
    tmax_prob = get_probability(data, name, month, day, range, 'TMAX', temp_max)
    tmin_prob = get_probability(data, name, month, day, range, 'TMIN', temp_min)
    prcp_prob = get_probability(data, name, month, day, range, 'PRCP', prcp)
    
    return {
        'TMAX': tmax_prob,
        'TMIN': tmin_prob,
        'PRCP': prcp_prob
    }

st.title('Weather Insurance Calculator')
