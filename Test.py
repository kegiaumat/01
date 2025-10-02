import os, json, sqlite3, io, streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

st.title("📂 Test đọc QLWorkXN.db từ Google Drive")

sa_json = os.environ.get("GDRIVE_SA")
folder_id = os.environ.get("GDRIVE_FOLDER_ID")

if not sa_json or not folder_id:
    st.error("❌ Chưa cấu hình GDRIVE_SA hoặc GDRIVE_FOLDER_ID trong secrets")
else:
    try:
        creds_info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds, cache_discovery=False)

        # === 1. Liệt kê file trong folder ===
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType, size)"
        ).execute()
        items = results.get("files", [])

        if not items:
            st.error("❌ Không có file nào trong folder!")
        else:
            st.subheader("📄 Danh sách file trong folder:")
            for f in items:
                st.write(f"👉 {f['name']} | ID: {f['id']} | Size: {f.get('size','N/A')}")

            # === 2. Tìm QLWorkXN.db ===
            db_file = next((f for f in items if f["name"] == "QLWorkXN.db"), None)
            if not db_file:
                st.error("❌ Không tìm thấy QLWorkXN.db trong folder!")
            else:
                file_id = db_file["id"]
                local_path = "/tmp/QLWorkXN.db"
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                with open(local_path, "wb") as f:
                    f.write(fh.getvalue())
                st.success(f"✅ Đã tải về: {local_path}")

                # === 3. Mở DB bằng sqlite3 ===
                try:
                    conn = sqlite3.connect(local_path)
                    cur = conn.cursor()
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cur.fetchall()
                    if tables:
                        st.subheader("📊 Các bảng trong QLWorkXN.db:")
                        for t in tables:
                            st.write(f"- {t[0]}")
                    else:
                        st.warning("⚠️ DB không có bảng nào!")
                    conn.close()
                except Exception as e:
                    st.error(f"⚠️ Lỗi đọc DB: {e}")

    except Exception as e:
        st.error(f"⚠️ Lỗi: {e}")
