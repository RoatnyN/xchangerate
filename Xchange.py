import os
import requests
import csv
import urllib3
import io

# 1. Setup & Silence SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This is the direct CSV download link for that specific dataset
CSV_URL = "https://data.mef.gov.kh/api/v1/public-datasets/pd_66a0cd503e0bd300012638fb4/download/csv"

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(REPO_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "ExchangeRate.csv")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

try:
    print("Attempting to fetch latest data...")
    # 2. Get the file (verify=False handles the SSL issue)
    response = requests.get(CSV_URL, headers=headers, timeout=30, verify=False)
    response.raise_for_status()

    # 3. Parse the CSV content from the response
    content = response.content.decode('utf-8')
    csv_data = list(csv.reader(io.StringIO(content)))

    if len(csv_data) > 1:
        # The first row is the header, the second row is usually the latest data
        latest_row = csv_data[1] 
        
        # Adjust these indices based on the MEF CSV structure
        # Usually: [Date, Rate, Currency, ...]
        date_text = latest_row[0]
        rate_text = latest_row[1]
        currency_pair = "KHR/USD"

        file_exists = os.path.isfile(file_path)
        final_row = [date_text, rate_text, currency_pair]

        with open(file_path, "a", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            if not file_exists:
                csvwriter.writerow(["Date", "Exchange Rate", "Currency Pair"])
            csvwriter.writerow(final_row)

        print(f"Success! Captured Rate: {rate_text} for Date: {date_text}")
    else:
        print("File downloaded but no data rows found.")

except Exception as e:
    print(f"Failed again: {e}")
    exit(1)
