import os, json, io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Lấy biến môi trường
sa_json = os.environ["GDRIVE_SA"]
folder_id = os.environ["GDRIVE_FOLDER_ID"]

creds_info = json.loads(sa_json)
scopes = ["https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)

# === 1. Tìm file hello.txt trong folder ===
results = service.files().list(
    q=f"'{folder_id}' in parents and name='hello.txt' and trashed=false",
    fields="files(id, name)"
).execute()
items = results.get("files", [])

if not items:
    raise Exception("❌ Không tìm thấy hello.txt trong folder. Hãy tạo file này trước trong Google Drive.")

file_id = items[0]["id"]
print("📂 Đã tìm thấy file:", items[0]["name"], "(", file_id, ")")

# === 2. Download nội dung file về ===
request = service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)

done = False
while not done:
    status, done = downloader.next_chunk()

content = fh.getvalue().decode("utf-8")
print("✅ Nội dung file hello.txt là:\n")
print(content)
