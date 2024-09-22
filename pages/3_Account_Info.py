import streamlit as st
import requests
import json
import pandas as pd
from nessie import get_customer_accounts  # Assuming this is a function in nessie.py

# Define the Nessie API key
api_key = st.secrets["NESSIE_API_KEY"]

def fetch_account_info(customer_id, api_key):
    """Fetch and display account information for a given customer."""
    accounts = get_customer_accounts(customer_id, api_key)
    
    if accounts:
        st.subheader("Account Information")
        st.json(accounts)  # Display raw account information in JSON format
        st.write(f"Number of accounts: {len(accounts)}")
        # Optionally, display specific account fields in a table
        account_list = []
        for account in accounts:
            account_list.append({
                "Account ID": account["_id"],
                "Type": account["type"],
                "Nickname": account["nickname"],
                "Balance": account["balance"],
                "Rewards": account.get("rewards", 0)
            })
        account_df = pd.DataFrame(account_list)
        st.write(account_df)

    else:
        st.error("No accounts found for this customer.")

def fetch_purchase_info(account_id, api_key):
    """Fetch and display purchase information for a given account."""
    url = f'http://api.nessieisreal.com/accounts/{account_id}/purchases?key={api_key}'
    response = requests.get(url)
    
    if response.status_code == 200:
        purchases = response.json()
        st.subheader("Purchase Information")
        if purchases:
            st.json(purchases)  # Display raw purchase information in JSON format
            # Display specific fields in a DataFrame
            purchase_list = []
            for purchase in purchases:
                purchase_list.append({
                    "Purchase ID": purchase["_id"],
                    "Merchant ID": purchase["merchant_id"],
                    "Amount": purchase["amount"],
                    "Date": purchase["purchase_date"],
                    "Status": purchase["status"]
                })
            purchase_df = pd.DataFrame(purchase_list)
            st.write(purchase_df)
        else:
            st.write("No purchases found.")
    else:
        st.error(f"Failed to fetch purchase data. Status code: {response.status_code}")

# Main App Logic
st.title("Account and Purchase Information")

# Input fields
customer_id = st.text_input("Enter Customer ID", "")
if customer_id:
    st.write("Fetching account information...")
    fetch_account_info(customer_id, api_key)
    
    # Fetch and display purchase info for each account
    account_id = st.text_input("Enter Account ID to view purchases", "")
    if account_id:
        fetch_purchase_info(account_id, api_key)
