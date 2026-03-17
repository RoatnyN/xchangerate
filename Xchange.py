import os
import requests
from bs4 import BeautifulSoup
import csv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. Setup Session with Retries (Helps with unstable connections)
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 2. Add Headers to mimic a real MacBook browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(REPO_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "ExchangeRate.csv")

url = "https://www.nbc.gov.kh/english/economic_research/exchange_rate.php"

try:
    # 3. Use the session and headers
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the date
    date_element = soup.find("font", color="#FF3300")
    date_text = date_element.get_text(strip=True) if date_element else "Date not found"

    # Extract the official exchange rate
    all_fonts = soup.find_all("font", color="#FF3300")
    rate_text = all_fonts[1].get_text(strip=True) if len(all_fonts) > 1 else "Rate not found"

    currency_pair = "KHR/USD"
    file_exists = os.path.isfile(file_path)
    row = [date_text, rate_text, currency_pair]

    with open(file_path, "a", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        if not file_exists:
            csvwriter.writerow(["Date", "Exchange Rate", "Currency Pair"])
        csvwriter.writerow(row)

    print(f"Success! Saved to {file_path}")

except Exception as e:
    print(f"Error during scraping: {e}")
    # This prevents GitHub Actions from showing 'Success' when it actually failed
    exit(1)
