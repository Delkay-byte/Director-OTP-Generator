import json
import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

OWNER_SECRET = "gT9sccN6Z#KjHEdaOv1ZapaXV2dG1cpq"
GOOGLE_SHEETS_ID = "1HELDHCGfPB-0MNg7auDezKdhITszY0lIvFvrVVY8PS0"
WORKSHEET_NAME = "APP_CONFIG"
ANALYSER_CONFIG_PATH = Path(__file__).parent.parent / "EduPulse-Analyzer" / "app_config.json"

SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "edupulse-auth-494716",
    "private_key_id": "16039b097171f18761fd02cd0812feb3036b9ec1",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7Zb9JUZcw2DGI\n"
        "7MMY/RhRgEaKL19rIsol6fEXWfH0oWm1MazJO0T08a8PcKF9FHaf0EcelLHtfbB6\n"
        "yDfhF99JQ3ARwmNoi6pCai+8m/tsBNtP0jhzQFRxJW6utDfA9aM0LuEEzH7Z6yLe\n"
        "yQntNCchrsdBYWQW/kXrXBIiKLuKAY9DK7m93DX0IDomIIAWMmAshLV/m9oDvnAl\n"
        "h1zi5zG5Yud+21DxENkAN9uzplOFqwE1+Vp7z/w3vKNdXqdBLYRK8rHVLKHP0SEo\n"
        "TJb2JMTF8BcPsi0LDwq24vA8/BBb9s0+ZVG4nrj81giD9TOrNksBfMgz+x9NHxE8\n"
        "Ldy2/XV5AgMBAAECggEAC7NLPZTNbbBr7FaLCmAAEROjI9zYFnB8QmCAS/LS2XEs\n"
        "EFL/DKvpjukZoutHe++nhewrSpiiYNeGia3/ViunRnPiVwuF6SjCO0YVv68WBD0r\n"
        "48iWe3SuaQebKOeJ7R9xHpCYPlRVzb2hhlszRlcJo+/dk0KVTR24aBzuKWmVZwT9\n"
        "OWPTpfxczhfKL7cwIO94OCOY+hs99NLnXHx5oeii+20xicMDF6f78b5Z+dtFCz01\n"
        "xk+iZLvXwBFcFGvsIe/JGKlTdAdjgvTjsnBWRNtljNf6F3GS7/S0TNJx0nseF64U\n"
        "RAy6IfRrl/jPL9FRyW15+SiCbf/eVHaaQTaL3stzQQKBgQDs4oPwHPXMo++9mE1F\n"
        "rRLqQSzUkCxgfI74mXUygHE6WrQ4+aDpP3+RRVcL8OT0Lyibc7ESidUqCCcsbwXA\n"
        "pTRpqTfa6+WvfA9vE8G3dSU0VCaKTeWzkmVX/ofWCXcfxaibWPm1Eqza6YSnB1No\n"
        "CPodl0f+RHO7v1J1fTAFxG/FQQKBgQDKhPBTt4AQRfJUD0yeMt/nDsXxdG5CNd69\n"
        "xe+zmbHmkVbudm3JRghU0JuubNVKEOJiSQx7QVF+yYNj6PF5E/1bMzmXwVEsUS6d\n"
        "tAlyz98/mRlAV15i/mPoodVhaxI51m369THK0vCe+sabK3jFYquTuG07FI4qB6kb\n"
        "GsavZOYKOQKBgHOZfuV4XINHJUGSx3LPKUHkGGqLCPz1DBhJWyYQBDGD/hsnxtzM\n"
        "vgY4nmgXYMPBF8H0zV7MoJfobqWCcH44oMFHcRiGsgnXMvjz3T8YDdXhkwU/Sm89\n"
        "a/NrJQLQj6+Tl9pnq0QwHuaduryAGLXWW6iBIQL2iLwAe88WDo9h82GBAoGBAIAm\n"
        "1Wk0Yh5qFKkqsUIeUV8GEy3yjl7pddTCrycIZ/HOIKNvX5OQ9G6vPwSGLAXdX1Pw\n"
        "g6xvLeG8JJ+RZVRH2PfgF163XuVbTdNPfPchIVU+TSNQ5hJghdpMphkqRvNAhIHc\n"
        "rLB7APapHApO3PKSuJ4Wg1Bydm+UP2c+b2HHyGXJAoGBAIbW6SuUok0IJdQuLJCz\n"
        "L2sbQC6/N+CEA41K5UEh9pTpNmF0cH1bYDWniM9RUyVxL6/LP71HgpQDCEmoH1Nt\n"
        "QRw5H2GLJOH5Yz0n+AuHdUHbaUasTOH5HM+6LIMVz2Tb1QC4ItZmv8wpRMhaWp7N\n"
        "ukSRUBC/yMaqz7jrcqU1+gfd\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "client_email": "edupulse-robot@edupulse-auth-494716.iam.gserviceaccount.com",
    "client_id": "104247551963153323152",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/edupulse-robot%40edupulse-auth-494716.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}

APP_CONFIG_HEADERS = [
    "district_name", "director_username", "headteacher_security_key",
    "director_registration_key", "director_registration_key_created_at",
    "smtp_host", "smtp_port", "smtp_username", "smtp_password",
    "smtp_sender_email", "smtp_use_tls",
]


def generate_director_key():
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(random.choice(chars) for _ in range(8))
    return f"DIRECTOR-{random_part}"


def get_google_sheet():
    if gspread is None or Credentials is None:
        raise RuntimeError("gspread or google-auth not installed.")
    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEETS_ID)


def write_otp_to_sheet(new_key, now_text):
    sheet = get_google_sheet()
    try:
        ws = sheet.worksheet(WORKSHEET_NAME)
    except Exception:
        ws = sheet.add_worksheet(title=WORKSHEET_NAME, rows=100, cols=20)
    existing = ws.get_all_records(default_blank="")
    row = existing[-1] if existing else {}
    for col in APP_CONFIG_HEADERS:
        row.setdefault(col, "")
    row["director_registration_key"] = new_key
    row["director_registration_key_created_at"] = now_text
    ws.clear()
    ws.update("A1", [APP_CONFIG_HEADERS, [str(row.get(col, "")) for col in APP_CONFIG_HEADERS]])


def write_otp_to_local_config(new_key, now_text):
    config = {}
    if ANALYSER_CONFIG_PATH.is_file():
        try:
            with open(ANALYSER_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass
    config["director_registration_key"] = new_key
    config["director_registration_key_created_at"] = now_text
    ANALYSER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ANALYSER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def read_current_otp_from_sheet():
    try:
        sheet = get_google_sheet()
        ws = sheet.worksheet(WORKSHEET_NAME)
        existing = ws.get_all_records(default_blank="")
        if existing:
            row = existing[-1]
            return row.get("director_registration_key", ""), row.get("director_registration_key_created_at", "")
    except Exception:
        pass
    return "", ""


st.set_page_config(page_title="Director OTP Generator", page_icon="🔐", layout="centered")
st.title("🔐 Director One-Time Key Generator")
st.caption(
    "Generates a one-time director registration key and saves it to **Google Sheets** "
    "(so the Streamlit Cloud analyser can read it) and to the local `app_config.json` as backup."
)

current_key, current_created = read_current_otp_from_sheet()

if current_key:
    st.info(
        f"**Active OTP in Google Sheets:** `{current_key}`"
        + (f"  \n**Generated:** {current_created}" if current_created else "")
    )
else:
    st.info("No active OTP found in Google Sheets.")

st.markdown("---")
owner_passphrase = st.text_input("Owner Passphrase", type="password")

if st.button("Generate New Director OTP", type="primary"):
    if owner_passphrase.strip() != OWNER_SECRET:
        st.error("Invalid owner passphrase.")
    else:
        new_key = generate_director_key()
        now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        sheet_ok = False
        local_ok = False
        sheet_err = ""
        local_err = ""

        with st.spinner("Connecting to Google Sheets..."):
            try:
                write_otp_to_sheet(new_key, now_text)
                sheet_ok = True
            except Exception as exc:
                sheet_err = str(exc)

        try:
            write_otp_to_local_config(new_key, now_text)
            local_ok = True
        except Exception as exc:
            local_err = str(exc)

        if sheet_ok:
            st.success(f"✅ OTP written to Google Sheets: `{new_key}`")
        else:
            st.error(f"❌ Google Sheets write failed:")
            st.code(sheet_err)

        if local_ok:
            st.success("✅ OTP written to local app_config.json")
        else:
            st.warning(f"⚠️ Local config write skipped/failed: {local_err}")

        if sheet_ok:
            st.rerun()