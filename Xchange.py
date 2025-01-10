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

# SharePoint access credentials (hardcoded for testing)
sharepoint_url = "https://minimumwage.sharepoint.com/sites/DATATEAM/Shared%20Documents/Economics/Economic/scrapping"
username = "Roatnynuon@minimumwage.onmicrosoft.com"  # Replace with your SharePoint email
password = "Nn@2024!!mnw"  # Replace with your SharePoint password

# Define a unique filename
csv_filename = f"exchange_rate_data_{date_text.replace('/', '-')}.csv"
csv_file_path = os.path.join(tempfile.gettempdir(), csv_filename)

# Write the data to the CSV file
with open(csv_file_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Date", "Exchange Rate", "Currency Pair"])
    csv_writer.writerow(data_to_upload)

# Upload the CSV file to SharePoint
upload_url = f"{sharepoint_url}/{csv_filename}"
print(f"Upload URL: {upload_url}")  # Debugging output

with open(csv_file_path, 'rb') as file:
    headers = {
        'Content-Type': 'application/octet-stream',
    }
    response = requests.put(upload_url, auth=(username, password), headers=headers, data=file)

    # Check if the upload was successful
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")  # Log the response content
    if response.status_code in [200, 201]:
        print("File uploaded successfully to SharePoint.")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

# Clean up
os.remove(csv_file_path)
