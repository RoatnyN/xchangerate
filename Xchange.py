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
tenant_id = os.environ['TENANT_ID']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
site_id = os.environ['SITE_ID']
drive_id = os.environ['DRIVE_ID']

# Define the CSV filename
csv_filename = "exchange_rate_data.csv"
csv_file_path = os.path.join(tempfile.gettempdir(), csv_filename)

# Write the data to the CSV file
with open(csv_file_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Date", "Exchange Rate", "Currency Pair"])
    csv_writer.writerow(data_to_upload)

# Function to get access token
def get_access_token(tenant_id, client_id, client_secret):
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json().get('access_token')

# Get the access token
access_token = get_access_token(tenant_id, client_id, client_secret)

# Upload the CSV file to SharePoint
upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{csv_filename}:/content"
with open(csv_file_path, 'rb') as file:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
    }
    response = requests.put(upload_url, headers=headers, data=file)

    # Check if the upload was successful
    if response.status_code in [200, 201]:
        print("File uploaded successfully to SharePoint.")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

# Clean up
os.remove(csv_file_path)
