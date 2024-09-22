import streamlit as st
from Main import load_data, get_probability, weather_probability
import requests
import json

def get_api_key():
    """Fetch the API key from Streamlit secrets."""
    return st.secrets["NESSIE_API_KEY"]

def delete_data(api_key):
    """Delete data using Nessie API."""
    categories = ["Accounts", "Customers", "Purchases", ]
    for i in categories:
        url = f'http://api.nessieisreal.com/data?type={i}&key={api_key}'
        response = requests.delete(url)
        print(response.content)


def get_customer_accounts(customer_id, api_key):
    """Fetch customer accounts using Nessie API."""
    url = f'http://api.nessieisreal.com/customers/{customer_id}/accounts?key={api_key}'
    response = requests.get(url)
    return json.loads(response.content)

def get_customers(api_key):
    """Fetch customer accounts using Nessie API."""
    url = f'http://api.nessieisreal.com/customers?key={api_key}'
    response = requests.get(url)
    return json.loads(response.content)

def get_merchants(api_key):
    """Fetch merchants using Nessie API."""
    url = f'http://api.nessieisreal.com/merchants?key={api_key}'
    response = requests.get(url)
    return json.loads(response.content)

def create_customer(api_key, first_name, last_name, street_number, street_name, city, state, zip_code):
    """Create a customer using the Nessie API."""
    url = f'http://api.nessieisreal.com/customers?key={api_key}'
    
    # Payload based on the provided structure
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "address": {
            "street_number": street_number,
            "street_name": street_name,
            "city": city,
            "state": state,
            "zip": zip_code
        }
    }
    
    response = requests.post(
        url, 
        data=json.dumps(payload), 
        headers={'content-type': 'application/json'}
    )

def create_account(customer_id, api_key, account_type, nickname, rewards, balance):
    """Create a new account for the customer."""
    url = f'http://api.nessieisreal.com/customers/{customer_id}/accounts?key={api_key}'
    payload = {
        "type": account_type,
        "nickname": nickname,
        "rewards": rewards,
        "balance": balance
    }
    response = requests.post(
        url, 
        data=json.dumps(payload), 
        headers={'content-type': 'application/json'}
    )
    return response.text

def create_merchant(api_key, merchant_name, category, street_number, street_name, city, state, zip_code, lat, lng):
    """Create a merchant using the Nessie API."""
    url = f'http://api.nessieisreal.com/merchants?key={api_key}'
    payload = {
        "name": merchant_name,
        "category": category,
        "address": {
            "street_number": street_number,
            "street_name": street_name,
            "city": city,
            "state": state,
            "zip": zip_code
        },
        "geocode": {
            "lat": lat,
            "lng": lng
        }
    }
    response = requests.post(
        url, 
        data=json.dumps(payload), 
        headers={'content-type': 'application/json'}
    )
    return response.text

def create_purchase(account_id, api_key, merchant_id, medium, purchase_date, amount, status, description):
    """Create a purchase for an account."""
    url = f'http://api.nessieisreal.com/accounts/{account_id}/purchases?key={api_key}'
    payload = {
        "merchant_id": merchant_id,
        "medium": medium,
        "purchase_date": purchase_date,
        "amount": amount,
        "status": status,
        "description": description
    }
    response = requests.post(
        url, 
        data=json.dumps(payload), 
        headers={'content-type': 'application/json'}
    )
    return response.text
