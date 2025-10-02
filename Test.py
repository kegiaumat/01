import os, json, streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.title("📂 List toàn bộ file trong folder Database")

sa_json = os.environ.get("GDRIVE_SA")
folder_id = os.environ.get("GDRIVE_FOLDER_ID")

if not sa_json or not folder_id:
    st.error("❌ Chưa cấu hình GDRIVE_SA hoặc GDRIVE_FOLDER_ID")
else:
    creds_info = json.loads(sa_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType, size)"
    ).execute()

    items = results.get("files", [])

    if not items:
        st.error("❌ Không tìm thấy file nào trong folder!")
    else:
        for f in items:
            st.write(f"📄 {f['name']}  |  ID: {f['id']}  |  Type: {f['mimeType']}  |  Size: {f.get('size', 'N/A')}")
