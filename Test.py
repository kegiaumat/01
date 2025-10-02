import os, json, io, streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

st.title("📂 Test đọc file hello.txt từ Google Drive")

# Lấy biến môi trường
sa_json = os.environ.get("GDRIVE_SA")
folder_id = os.environ.get("GDRIVE_FOLDER_ID")

if not sa_json or not folder_id:
    st.error("❌ Chưa cấu hình GDRIVE_SA hoặc GDRIVE_FOLDER_ID trong secrets!")
else:
    try:
        creds_info = json.loads(sa_json)
        scopes = ["https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=scopes
        )
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)

        # === 1. Tìm file hello.txt trong folder ===
        results = service.files().list(
            q=f"'{folder_id}' in parents and name='hello.txt' and trashed=false",
            fields="files(id, name)"
        ).execute()
        items = results.get("files", [])

        if not items:
            st.error("❌ Không tìm thấy hello.txt trong folder. Hãy tạo file này trước.")
        else:
            file_id = items[0]["id"]
            st.success(f"Đã tìm thấy file: {items[0]['name']} (ID: {file_id})")

            # === 2. Download nội dung file ===
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            content = fh.getvalue().decode("utf-8")

            st.subheader("📖 Nội dung hello.txt:")
            st.code(content)

    except Exception as e:
        st.error(f"⚠️ Lỗi: {e}")
