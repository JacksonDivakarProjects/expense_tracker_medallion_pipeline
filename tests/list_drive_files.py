import sys
from pathlib import Path

# Add the 'src' directory to the path so we can use our existing modules
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir / "src"))

from gcp_drive import authenticate_gcp_from_env
from googleapiclient.discovery import build

def search_drive():
    print("Authenticating and searching Drive for 'Expense'...")
    creds = authenticate_gcp_from_env()
    service = build('drive', 'v3', credentials=creds)
    
    # Query for anything containing the word Expense (ignoring the file type)
    results = service.files().list(
        q="name contains 'Expense'", 
        fields="files(id, name, mimeType)"
    ).execute()
    
    items = results.get('files', [])
    
    if not items:
        print("\n✕ No files containing 'Expense' were found in this Google Account.")
        print("Are you sure you authenticated with the correct email address?")
    else:
        print("\n✓ Found these files:")
        for item in items:
            print(f"Name: '{item['name']}' | Type: {item['mimeType']}")

if __name__ == '__main__':
    search_drive()