import os
import requests
from bs4 import BeautifulSoup
import csv
import urllib3

# 1. Setup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL = "https://www.tax.gov.kh/en/exchange-rate"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(REPO_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "ExchangeRate.csv")

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

try:
    response = requests.get(URL, headers=headers, timeout=30, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Get all rows from the GDT table
    all_rows = soup.find("table").find("tbody").find_all("tr")

    # 2. Check existing dates in your CSV to avoid duplicates
    existing_dates = set()
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if row:
                    existing_dates.add(row[0])

    # 3. Process rows (reversed to keep chronological order: oldest to newest)
    new_entries = []
    for row in reversed(all_rows):
        cols = row.find_all("td")
        if len(cols) >= 3:
            date_text = cols[0].get_text(strip=True)
            rate_text = cols[2].get_text(strip=True)
            currency_pair = cols[1].get_text(strip=True)

            # Only add if we don't have this date yet
            if date_text not in existing_dates:
                new_entries.append([date_text, rate_text, currency_pair])

    # 4. Save only the new data
    file_exists = os.path.isfile(file_path)
    if new_entries:
        with open(file_path, "a", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            if not file_exists:
                csvwriter.writerow(["Date", "Exchange Rate", "Currency Pair"])
            for entry in new_entries:
                csvwriter.writerow(entry)
                print(f"Added: {entry[0]} -> {entry[1]}")
    else:
        print("No new exchange rates found today.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
