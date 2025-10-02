import os, json, sqlite3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# === 1. Kiểm tra biến môi trường (Secrets) ===
print("🔎 DB_BACKEND:", os.environ.get("DB_BACKEND"))
print("🔎 DB_LOCAL_PATH:", os.environ.get("DB_LOCAL_PATH"))
print("🔎 GDRIVE_FOLDER_ID:", os.environ.get("GDRIVE_FOLDER_ID"))
print("🔎 Có GDRIVE_SA:", "YES" if os.environ.get("GDRIVE_SA") else "NO")

# === 2. Kết nối tới Google Drive ===
sa_json = os.environ.get("GDRIVE_SA")
folder_id = os.environ.get("GDRIVE_FOLDER_ID")

if not sa_json or not folder_id:
    raise Exception("❌ Chưa có GDRIVE_SA hoặc GDRIVE_FOLDER_ID trong secrets!")

creds_info = json.loads(sa_json)
scopes = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)

# === 3. Liệt kê file trong folder ===
print("\n📂 Danh sách file trong folder:")
results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name)").execute()
items = results.get("files", [])
for f in items:
    print("   -", f["name"], "(", f["id"], ")")

# === 4. Thử tạo một file test ===
print("\n✍️ Upload file test.txt vào folder...")
local_file = "/tmp/test_drive.txt"
with open(local_file, "w", encoding="utf-8") as f:
    f.write("Hello from test_drive.py!")

file_metadata = {"name": "test_drive.txt", "parents": [folder_id]}
media = MediaFileUpload(local_file, mimetype="text/plain")
uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
print("✅ Đã upload test_drive.txt với ID:", uploaded.get("id"))

# === 5. Thử tạo 1 database SQLite local ===
print("\n🗄️ Tạo file tasks_test.db local và insert dữ liệu...")
db_path = "/tmp/tasks_test.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, last_seen TIMESTAMP)")
c.execute("INSERT INTO users (username, last_seen) VALUES (?, datetime('now'))", ("tester",))
conn.commit()
conn.close()
print("✅ DB local đã tạo:", db_path)

# === 6. Upload DB này lên Google Drive ===
print("\n☁️ Upload tasks_test.db lên Drive...")
file_metadata = {"name": "tasks_test.db", "parents": [folder_id]}
media = MediaFileUpload(db_path, mimetype="application/x-sqlite3")
uploaded_db = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
print("✅ Đã upload tasks_test.db với ID:", uploaded_db.get("id"))
