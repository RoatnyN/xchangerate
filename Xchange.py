import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Define the URL
url = "https://www.nbc.gov.kh/english/economic_research/exchange_rate.php"

# Send a GET request
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Extract the date
date_element = soup.find("font", color="#FF3300")
date_text = date_element.get_text(strip=True) if date_element else "Date not found"

# Extract the official exchange rate
rate_element = soup.find_all("font", color="#FF3300")[1]
rate_text = rate_element.get_text(strip=True) if rate_element else "Rate not found"

# Extract the currency pair
currency_pair = "KHR/USD"  # Static value as it is fixed in the HTML structure

# Define the folder path in your OneDrive
folder_path = os.path.expanduser("~/OneDrive/MNW_Dataset")  # Adjust this as needed
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "Xchange.csv")

# Check if the file exists
file_exists = os.path.isfile(file_path)

# Prepare the row to append
row = [date_text, rate_text, currency_pair]

# Write or append the data
with open(file_path, "a", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    if not file_exists:
        csvwriter.writerow(["Date", "Exchange Rate", "Currency Pair"])
    csvwriter.writerow(row)

# Upload to SharePoint
sharepoint_url = os.environ['SHAREPOINT_URL']
username = os.environ['SHAREPOINT_USERNAME']
password = os.environ['SHAREPOINT_PASSWORD']

with open(file_path, 'rb') as file:
    requests.post(sharepoint_url, auth=(username, password), files={'file': file})

print(f"Exchange rate details saved to {file_path} and uploaded to SharePoint.")
