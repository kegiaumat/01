import os, json, sqlite3, io, streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

st.title("📂 Test đọc DB từ Google Drive")

sa_json = os.environ.get("GDRIVE_SA")
folder_id = os.environ.get("GDRIVE_FOLDER_ID")
db_name = "QLWorkXN.db"   # tên file db bạn đang dùng

# === 1. Tải DB về ===
creds_info = json.loads(sa_json)
scopes = ["https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)

results = service.files().list(
    q=f"'{folder_id}' in parents and name='{db_name}' and trashed=false",
    fields="files(id, name)"
).execute()
items = results.get("files", [])

if not items:
    st.error(f"❌ Không tìm thấy {db_name} trong folder")
else:
    file_id = items[0]["id"]
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    local_path = f"/tmp/{db_name}"
    with open(local_path, "wb") as f:
        f.write(fh.getvalue())
    st.success(f"✅ Đã tải {db_name} về {local_path}")

    # === 2. Đọc schema và dữ liệu user ===
    conn = sqlite3.connect(local_path)
    c = conn.cursor()

    st.subheader("📌 Các bảng trong DB:")
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    st.write(tables)

    if ("users",) in tables:
        st.subheader("👥 Dữ liệu trong bảng users:")
        users = c.execute("SELECT * FROM users").fetchall()
        st.write(users)
    else:
        st.error("❌ Bảng users không tồn tại trong DB")
