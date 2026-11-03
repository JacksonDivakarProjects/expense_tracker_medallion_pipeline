import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

# Load your .env file
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

client_id = os.getenv("GCP_CLIENT_ID")
client_secret = os.getenv("GCP_CLIENT_SECRET")

if not client_id or not client_secret:
    print("Error: GCP_CLIENT_ID and GCP_CLIENT_SECRET must be in your .env file.")
    sys.exit(1)

# Reconstruct the client config required by Google's flow
client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

print("Opening browser for authentication...")
flow = InstalledAppFlow.from_client_config(
    client_config, 
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)

# This opens the browser
creds = flow.run_local_server(port=0)

print("\n--- SUCCESS ---")
print("Copy the string below and paste it as your GCP_REFRESH_TOKEN in your .env file:\n")
print(creds.refresh_token)
print("\n----------------")