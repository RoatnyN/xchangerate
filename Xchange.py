import os
import requests
import csv

# MEF Public API for NBC Exchange Rates
# This is much less likely to be blocked than the main website
API_URL = "https://data.mef.gov.kh/api/v1/public-datasets/pd_66a0cd503e0bd300012638fb4/json?page=1&page_size=1"

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(REPO_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "ExchangeRate.csv")

try:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    # The API returns a list of records. We take the latest one.
    record = data['data'][0]
    
    # Mapping fields from the API (adjust keys based on actual API response if needed)
    date_text = record.get('date', 'N/A')
    rate_text = record.get('rate', 'N/A')
    currency_pair = "KHR/USD"

    file_exists = os.path.isfile(file_path)
    row = [date_text, rate_text, currency_pair]

    with open(file_path, "a", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        if not file_exists:
            csvwriter.writerow(["Date", "Exchange Rate", "Currency Pair"])
        csvwriter.writerow(row)

    print(f"Success via API! Data saved to {file_path}")

except Exception as e:
    print(f"API also failed: {e}")
    exit(1)
