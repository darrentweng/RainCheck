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


st.title('Weather Insurance Calculator')
