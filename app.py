import json
import os
import random
from datetime import datetime, timezone

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:  # pragma: no cover - optional dependency
    gspread = None
    Credentials = None


SHEETS_ID_ENV = "EDUPULSE_GOOGLE_SHEETS_ID"
SERVICE_ACCOUNT_JSON_ENV = "EDUPULSE_GOOGLE_SERVICE_ACCOUNT_JSON"
OWNER_SECRET_ENV = "EDUPULSE_OWNER_SECRET"
WORKSHEET_NAME = "APP_CONFIG"


def load_owner_secret():
    return os.environ.get(OWNER_SECRET_ENV, "").strip() or "BloomCore-Owner-Set-Me"


def generate_director_key():
    return f"DIRECTOR-{random.randint(100000, 999999)}"


def get_google_sheet():
    sheet_id = os.environ.get(SHEETS_ID_ENV, "").strip()
    creds_json = os.environ.get(SERVICE_ACCOUNT_JSON_ENV, "").strip()
    if not (sheet_id and creds_json and gspread is not None and Credentials is not None):
        return None
    try:
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(
            creds_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly",
            ],
        )
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id)
    except Exception:
        return None


def upsert_key_to_sheet(new_key):
    sheet = get_google_sheet()
    if sheet is None:
        raise RuntimeError("Google Sheet connection failed. Check environment variables and service account credentials.")

    now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        try:
            ws = sheet.worksheet(WORKSHEET_NAME)
        except Exception:
            ws = sheet.add_worksheet(title=WORKSHEET_NAME, rows=100, cols=20)
        headers = [
            "district_name",
            "director_username",
            "headteacher_security_key",
            "director_registration_key",
            "director_registration_key_created_at",
            "smtp_host",
            "smtp_port",
            "smtp_username",
            "smtp_password",
            "smtp_sender_email",
            "smtp_use_tls",
        ]
        existing = ws.get_all_records(default_blank="")
        row = existing[-1] if existing else {}
        for key in headers:
            row.setdefault(key, "")
        row["director_registration_key"] = new_key
        row["director_registration_key_created_at"] = now_text
        ws.clear()
        ws.update("A1", [headers, [str(row.get(col, "")) for col in headers]])
    except Exception as exc:
        raise RuntimeError(f"Failed to write key to APP_CONFIG sheet: {exc}") from exc


st.set_page_config(page_title="Director OTP Generator", page_icon="🔐", layout="centered")
st.title("🔐 Director One-Time Key Generator")
st.caption("This app writes a new one-time director registration key into your shared Google Sheet backend.")

owner_passphrase = st.text_input("Owner Passphrase", type="password")
if st.button("Generate New Director OTP", type="primary"):
    if owner_passphrase.strip() != load_owner_secret():
        st.error("Invalid owner passphrase.")
    else:
        generated_key = generate_director_key()
        try:
            upsert_key_to_sheet(generated_key)
            st.success(f"New director OTP generated and saved: {generated_key}")
        except Exception as exc:
            st.error(str(exc))
