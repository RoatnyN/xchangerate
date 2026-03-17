import os
import requests
import csv
import urllib3

# This hides the warning message that appears when you use verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://data.mef.gov.kh/api/v1/public-datasets/pd_66a0cd503e0bd300012638fb4/json?page=1&page_size=1"

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(REPO_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "ExchangeRate.csv")

try:
    # verify=False skips the SSL certificate check
    response = requests.get(API_URL, timeout=30, verify=False)
    response.raise_for_status()
    data = response.json()

    # Get the latest record
    record = data['data'][0]
    
    # Check the actual keys in the MEF API (usually 'date' and 'value' or 'rate')
    # Use .get() to avoid crashing if a key is missing
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

    print(f"Success! Captured {rate_text} for {date_text}")

except Exception as e:
    print(f"Failed: {e}")
    exit(1)
