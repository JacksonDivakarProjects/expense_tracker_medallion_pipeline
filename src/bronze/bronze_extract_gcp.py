import io
import os
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import config

def authenticate_gcp_from_env():
    """Authenticates with Google Cloud using config variables."""
    if not all([config.GCP_CLIENT_ID, config.GCP_CLIENT_SECRET, config.GCP_REFRESH_TOKEN]):
        raise ValueError("Missing Google Cloud credentials in .env file.")

    creds = Credentials(
        token=None,  
        refresh_token=config.GCP_REFRESH_TOKEN,
        client_id=config.GCP_CLIENT_ID,
        client_secret=config.GCP_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return creds

def sync_expense_folder(service, folder_name="Expense Data"):
    """Finds a folder by name, downloads missing Excel files, and converts them to CSV."""
    # 1. Find the exact Folder ID
    folder_query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    folders = service.files().list(q=folder_query, fields="files(id, name)").execute().get('files', [])
    
    if not folders:
        raise FileNotFoundError(f"Could not find the folder: {folder_name}")
    
    folder_id = folders[0]['id']
    print(f"  -> Found Drive folder '{folder_name}'. Scanning for files...")
    
    # 2. List all files inside this specific folder
    file_query = f"'{folder_id}' in parents and trashed = false"
    files = service.files().list(q=file_query, fields="files(id, name, mimeType)").execute().get('files', [])
    
    if not files:
        print("  -> No files found in the folder.")
        return

    # 3. Process each file
    for item in files:
        file_id = item['id']
        file_name = item['name']
        
        # We only want the Excel files
        if 'spreadsheetml.sheet' not in item['mimeType']:
            continue
            
        # Determine the final CSV name and path
        csv_name = file_name.replace(' ', '_').replace('.xlsx', '.csv')
        csv_path = os.path.join(config.RAW_DATA_DIR, csv_name)
        
        # Skip if the file already exists locally
        if os.path.exists(csv_path):
            print(f"  -> Skipping {file_name} (Already exists locally)")
            continue
            
        print(f"  -> Downloading {file_name}...")
        request = service.files().get_media(fileId=file_id)
        
        # Save as a temporary Excel file first
        temp_xlsx_path = os.path.join(config.RAW_DATA_DIR, file_name)
        
        with io.FileIO(temp_xlsx_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        
        # Convert to CSV using pandas
        df = pd.read_excel(temp_xlsx_path)
        df.to_csv(csv_path, index=False)
        
        # Clean up the temporary Excel file
        os.remove(temp_xlsx_path)
        print(f"  -> Converted and saved to {csv_path}")

def extract_from_drive():
    """Main function to trigger the extraction."""
    creds = authenticate_gcp_from_env()
    service = build('drive', 'v3', credentials=creds)
    sync_expense_folder(service)