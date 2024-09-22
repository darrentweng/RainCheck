from nessie import get_customer_accounts, get_api_key, delete_data, get_customers, get_merchants, create_account, create_merchant, create_purchase, create_customer

# customer_id = '66ef34ec9683f20dd518a157'
api_key = get_api_key()

delete_data(api_key)

create_customer(api_key, "John", "Doe", "3330", "Walnut Street", "Philadelphia", "PA", "19104")

customers = get_customers(api_key)

customer_id = customers[0]["_id"]

create_account(customer_id, api_key, "Savings", "test", 10000, 10000)

accounts = get_customer_accounts(customer_id, api_key)

account_id = accounts[0]["_id"]

#create_merchant(api_key, "JakeFarm", "insurance", "3330", "Walnut St", "Philadelphia", "PA", "19104", 40, -75)

merchants = get_merchants(api_key)
merchant_id = merchants[0]["_id"]
create_purchase(account_id, api_key, merchant_id, "balance", "2024-09-22", 20, "pending", "buying insurance")