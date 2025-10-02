import os, json, datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Lấy biến môi trường
sa_json = os.environ["GDRIVE_SA"]
folder_id = os.environ["GDRIVE_FOLDER_ID"]

# Parse credentials
creds_info = json.loads(sa_json)
scopes = ["https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(
    creds_info, scopes=scopes
)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)

# === 1. Kiểm tra có file hello.txt chưa trong folder ===
results = service.files().list(
    q=f"'{folder_id}' in parents and name='hello.txt' and trashed=false",
    fields="files(id, name)"
).execute()
items = results.get("files", [])

if not items:
    raise Exception("❌ Chưa có file hello.txt trong folder, hãy tạo file rỗng trước!")

file_id = items[0]["id"]

# === 2. Ghi thời gian khởi động vào file local ===
local_file = "/tmp/hello.txt"
with open(local_file, "w", encoding="utf-8") as f:
    f.write("Khởi động lúc: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# === 3. Upload ghi đè lên Google Drive ===
media = MediaFileUpload(local_file, mimetype="text/plain", resumable=True)
updated = service.files().update(
    fileId=file_id,
    media_body=media
).execute()

print("✅ File hello.txt đã được cập nhật lúc:", datetime.datetime.now())
