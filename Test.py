import os, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sa_json = os.environ["GDRIVE_SA"]
folder_id = os.environ["GDRIVE_FOLDER_ID"]

creds_info = json.loads(sa_json)
scopes = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)

# tạo file local
with open("/tmp/hello.txt", "w") as f:
    f.write("Hello Google Drive!")

# upload
file_metadata = {"name": "hello.txt", "parents": [folder_id]}
media = MediaFileUpload("/tmp/hello.txt", mimetype="text/plain")
uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
print("✅ Uploaded hello.txt with ID:", uploaded["id"])
