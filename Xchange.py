import os
import requests
from bs4 import BeautifulSoup
import csv
import urllib3

# 1. Setup & Silence SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# We use the Tax.gov.kh site because it's more stable for cloud scrapers
URL = "https://www.tax.gov.kh/en/exchange-rate"

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(REPO_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "ExchangeRate.csv")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

try:
    print(f"Connecting to GDT to fetch NBC rates...")
    response = requests.get(URL, headers=headers, timeout=30, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the first row in the exchange rate table
    # On GDT, the first <tr> after <thead> usually contains the latest rate
    table_row = soup.find("table").find("tbody").find("tr")
    cols = table_row.find_all("td")

    if len(cols) >= 3:
        # GDT Table Format: [Release Date, Symbol, Official Rate, Published By]
        date_text = cols[0].get_text(strip=True)
        rate_text = cols[2].get_text(strip=True)
        currency_pair = cols[1].get_text(strip=True) # Usually "USD/KHR"

        file_exists = os.path.isfile(file_path)
        final_row = [date_text, rate_text, currency_pair]

        with open(file_path, "a", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            if not file_exists:
                csvwriter.writerow(["Date", "Exchange Rate", "Currency Pair"])
            csvwriter.writerow(final_row)

        print(f"Success! Captured: {currency_pair} {rate_text} for {date_text}")
    else:
        print("Could not find data in the table.")

except Exception as e:
    print(f"Failed to scrape GDT: {e}")
    exit(1)
