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
GOOGLE_SHEETS_ID = "1Yn0yG4I40DBRUO3QLP3yIsYQXkStQxCXOmtTM2r0s6E"
WORKSHEET_NAME = "APP_CONFIG"
ANALYSER_CONFIG_PATH = Path(__file__).parent.parent / "EduPulse-Analyzer" / "app_config.json"

SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "edupulse-auth-494619",
    "private_key_id": "5d0e30a7bea7bbd9a284726105968316098878d9",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC14OkazWIY0y50\n"
        "+jydu9UzvB1IL29D2u/Uym9jV7i/n/NVCVy6hmr4osge/xQiDZhWBOx4gpaY+a2d\n"
        "kqPb6oXGwnShpU/MrVkcbQOdYknBju6kBU007a/I7a5SiIL2zUlsvmIHdN15acH/\n"
        "V7BqU2zdAKzmJcc66R5PvTg+DIK18oo0sEM00h4sjr39dfeMCwTft3HX+F/0IUxT\n"
        "SIonVytUtDMODsTySMSuFiD+1T+1LchGkYw0ZBg9daWni0+LTcqY60FTu7/3c21o\n"
        "8rc4wpKAyYF2sKhfVqCRqfYajIBxrraFxyQkDKpp29xun7CZQXNYLVFe+jkj6qQF\n"
        "L1E41H5BAgMBAAECggEAIdcT0CCUJrXOQEYZ9qgu6kYPNbHbtCaddnxm3rdA4OiQ\n"
        "FAuepPbjGtlgvkGsG4zngeO/Isn7XsGf38BbvAyF8P4XyMazEwxS1vLimAskWX7w\n"
        "YHS7EYTC7vHoPCN5qJV4GqNOpoAEQDWg+pM0eAgHKpSYVucDC2857FCy0PqvbE5A\n"
        "qM7wrlEpqlE7dC2sb+rWXJ1ky3SRWHt4gdj5H4NjHeg+b5JUP1viXx+3Pph5U8vz\n"
        "jRGgX8AdQDsgL55ETp5PtVIl5P2gqLRz2+R6wkQES+9c5TKr3wLjvg1sp7nwcUwz\n"
        "l9AZB3wDYuZuTUpCFpuH4fi3ps3Re0vR8W4bXg/SdQKBgQDjOcIibWslst9dGBkf\n"
        "9NfjSHytAVrmexksuCKxnbXk2qXyYndxI1jYj4GcVVL2fUPL8zWDeM3hYVn80yWL\n"
        "2m0HCVymPU/bcghkP7+4dShzF6BuYJdTi+e/xkN4ddK/bFA/8lRPkosExcqM9Tko\n"
        "2PSRFLO8mU3tRgm4YkW/fvDIPQKBgQDM6RU4Qs4cbGB10u6j6+1dyFcrwYDAzimY\n"
        "DJy+JzqsUcqaAVI/zVFfkpEhYOaNK+Y9yR5P198mD/NyUAzQGIOgRY9o2bSOZosm\n"
        "i7lQXS+N0454a2nT2TTSyDH5avUna9bmTsLxYaTF+AHFN2n51QTuXeTsN+4joOz2\n"
        "AJlCcqgqVQKBgFw8duSYu/TKnkbg4FoLfpMhOpLTyP1kHLz9Zf/pgAuNAe3ZMJj5\n"
        "ezg1UKyQKiQqhxnD+QYMRK5nYSry3vvdR4Kitzw4CTGQIX3oLsAGtsu5XINRrDva\n"
        "v9El/v9n/It9wTmj+btvRgVC8My1QmWlY+l8mNVG+c4GLy3snll0gvMVAoGBAI/f\n"
        "S93f0hXU5nlz68i+e0AwzTvUtpEpb7zphhhhNOoO16EAMn7Hq03ee/Yisl4Gp7dU\n"
        "Aetvl6eC5ZyqpgRqYejjTkkBKqwdRbB/xFKvyxbapprYWEq9pEAm/iewuIbASfgU\n"
        "7v1KYMX7V0rgmJEoxziSRoywzIzJjfc//lvQY1CtAoGAZiHA3n1OU/zvsTSJRps8\n"
        "P/foHMnDuVxpcpZoeaWw0ApDGo9ixpoonB6/R4DKTdZ3HVeZE4QZA/+b0QF+8Tph\n"
        "5L5TYMNOM0iWg3vtqLC4lnhSEVax3EGYRcd7hqXloecHFz21nGsd1xoSqWAkOoYA\n"
        "zR8aVF5sf6Fj15Ka76wNUJ0=\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "client_email": "edupulse-robot@edupulse-auth-494619.iam.gserviceaccount.com",
    "client_id": "103082176599383008136",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/edupulse-robot%40edupulse-auth-494619.iam.gserviceaccount.com",
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
        errors = []
        try:
            write_otp_to_sheet(new_key, now_text)
        except Exception as exc:
            errors.append(f"Google Sheets: {exc}")
        try:
            write_otp_to_local_config(new_key, now_text)
        except Exception as exc:
            errors.append(f"Local config: {exc}")
        if not errors:
            st.success(f"OTP generated and saved everywhere: `{new_key}`")
        elif len(errors) == 1:
            st.warning(f"OTP saved with one warning — {errors[0]}")
            st.success(f"Active OTP: `{new_key}`")
        else:
            st.error("Failed to save OTP to both destinations:")
            for e in errors:
                st.code(e)
        if errors == [] or len(errors) < 2:
            st.rerun()