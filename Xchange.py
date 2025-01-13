import os
import requests
import tempfile
import urllib.parse  # Make sure to import this

# Get environment variables
tenant_id = os.environ['TENANT_ID']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
sharepoint_url = os.environ['SHAREPOINT_URL']

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

# Get the access token
access_token = get_access_token(tenant_id, client_id, client_secret)

# Encode the folder path to ensure special characters are handled correctly
folder_path = "Shared%20Documents/Economics/Economic/scrapping"
encoded_folder_path = urllib.parse.quote(folder_path)

# Construct the upload URL
upload_url = f"{sharepoint_url}/_api/web/GetFolderByServerRelativeUrl('{encoded_folder_path}')/Files/add(overwrite=true,url='testfile.txt')"

# Create a simple plain text file
text_file_content = "This is a test file to check upload functionality."
text_filename = "testfile.txt"
text_file_path = os.path.join(tempfile.gettempdir(), text_filename)

with open(text_file_path, 'w') as file:
    file.write(text_file_content)

# Upload the text file to SharePoint
with open(text_file_path, 'rb') as file:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
    }
    response = requests.post(upload_url, headers=headers, data=file)

    if response.status_code in [200, 201]:
        print("Plain text file uploaded successfully to SharePoint.")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

# Remove the temporary file
os.remove(text_file_path)
