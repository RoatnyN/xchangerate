import os
import requests
from bs4 import BeautifulSoup
import csv
import tempfile
import urllib.parse

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

if date_text == "Date not found" or rate_text == "Rate not found":
    print("Scraping failed. Exiting without uploading.")
    exit()

# Prepare the data to upload
data_to_upload = [date_text, rate_text, "KHR/USD"]

# Write the data to a temporary CSV file
csv_filename = "exchange_rate_data.csv"
csv_file_path = os.path.join(tempfile.gettempdir(), csv_filename)

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
    response.raise_for_status()
    return response.json().get('access_token')

# Get environment variables
tenant_id = os.environ['TENANT_ID']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
sharepoint_url = os.environ['SHAREPOINT_URL']

# Get the access token
access_token = get_access_token(tenant_id, client_id, client_secret)

# Encode the folder path to ensure special characters are handled correctly
folder_path = "Shared%20Documents/Economics/Economic/scrapping"
encoded_folder_path = urllib.parse.quote(folder_path)

# Construct the upload URL
https://minimumwage.sharepoint.com/sites/DATATEAM/_api/web/GetFolderByServerRelativeUrl('Shared%20Documents/Economics/Economic/scrapping')/Files/add(overwrite=true,url='exchange_rate_data.csv')

# Upload the CSV file to SharePoint
with open(csv_file_path, 'rb') as file:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
    }
    response = requests.post(upload_url, headers=headers, data=file)

    if response.status_code in [200, 201]:
        print("File uploaded successfully to SharePoint.")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

# Remove the temporary file
os.remove(csv_file_path)
