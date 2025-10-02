import os, json, sqlite3, io, streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

st.title("👥 Kiểm tra bảng users trong QLWorkXN.db")

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
            fields="files(id, name, size)"
        ).execute()
        items = results.get("files", [])

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

            # === 2. Kiểm tra bảng users ===
            try:
                conn = sqlite3.connect(local_path)
                cur = conn.cursor()

                # Liệt kê các bảng
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cur.fetchall()]
                st.write("📊 Các bảng trong DB:", tables)

                if "users" in tables:
                    cur.execute("SELECT * FROM users LIMIT 10;")
                    rows = cur.fetchall()
                    if rows:
                        st.subheader("👥 10 user đầu tiên:")
                        for r in rows:
                            st.write(r)
                    else:
                        st.warning("⚠️ Bảng users không có dữ liệu.")
                else:
                    st.error("❌ Không có bảng users trong DB.")

                conn.close()
            except Exception as e:
                st.error(f"⚠️ Lỗi đọc DB: {e}")

    except Exception as e:
        st.error(f"⚠️ Lỗi: {e}")
