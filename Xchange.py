import os
import requests
from bs4 import BeautifulSoup
import csv
import tempfile 

# Define the URL
url = "https://www.nbc.gov.kh/english/economic_research/exchange_rate.php"

# Send a GET request
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Extract the date and rate
date_element = soup.find("font", color="#FF3300")
date_text = date_element.get_text(strip=True) if date_element else "Date not found"
rate_element = soup.find_all("font", color="#FF3300")[1]
rate_text = rate_element.get_text(strip=True) if rate_element else "Rate not found"

# Check for successful scraping
if date_text == "Date not found" or rate_text == "Rate not found":
    print("Scraping failed. Exiting without uploading.")
    exit()

# Prepare the data to upload
data_to_upload = [date_text, rate_text, "KHR/USD"]

# Upload to SharePoint
sharepoint_url = os.environ['SHAREPOINT_URL']
username = os.environ['SHAREPOINT_USERNAME']
password = os.environ['SHAREPOINT_PASSWORD']

# Define the CSV filename
csv_filename = "exchange_rate_data.csv"
csv_file_path = os.path.join(tempfile.gettempdir(), csv_filename)

# Write the data to the CSV file
with open(csv_file_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Date", "Exchange Rate", "Currency Pair"])
    csv_writer.writerow(data_to_upload)

# Upload the CSV file to SharePoint
upload_url = f"{sharepoint_url}/{csv_filename}"
with open(csv_file_path, 'rb') as file:
    headers = {
        'Content-Type': 'application/octet-stream',
    }
    response = requests.put(upload_url, auth=(username, password), headers=headers, data=file)

    # Check if the upload was successful
    if response.status_code in [200, 201]:
        print("File uploaded successfully to SharePoint.")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

# Clean up
os.remove(csv_file_path)
