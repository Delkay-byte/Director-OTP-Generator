import json
import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

OWNER_SECRET = "gT9sccN6Z#KjHEdaOv1ZapaXV2dG1cpq"
ANALYSER_CONFIG_PATH = Path(__file__).parent.parent / "EduPulse-Analyzer" / "app_config.json"


def generate_director_key():
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(random.choice(chars) for _ in range(8))
    return f"DIRECTOR-{random_part}"


def load_analyser_config():
    if ANALYSER_CONFIG_PATH.is_file():
        try:
            with open(ANALYSER_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_otp_to_analyser_config(new_key):
    config = load_analyser_config()
    config["director_registration_key"] = new_key
    config["director_registration_key_created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    ANALYSER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ANALYSER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


st.set_page_config(page_title="Director OTP Generator", page_icon="🔐", layout="centered")
st.title("🔐 Director One-Time Key Generator")
st.caption(
    "Generates a one-time director registration key and saves it directly to the "
    "EduPulse-Analyzer `app_config.json` on this machine. **Local use only — no internet required.**"
)

config_status = ANALYSER_CONFIG_PATH.is_file()
if config_status:
    st.success(f"EduPulse-Analyzer config found at: `{ANALYSER_CONFIG_PATH}`")
else:
    st.warning(
        f"Config file not found at `{ANALYSER_CONFIG_PATH}`. "
        "It will be created when you generate the first key."
    )

current_config = load_analyser_config()
current_key = current_config.get("director_registration_key", "")
current_created = current_config.get("director_registration_key_created_at", "")

if current_key:
    st.info(f"**Active OTP:** `{current_key}`" + (f"  \n**Generated:** {current_created}" if current_created else ""))
else:
    st.info("No active OTP. Generate one below.")

st.markdown("---")
owner_passphrase = st.text_input("Owner Passphrase", type="password")

if st.button("Generate New Director OTP", type="primary"):
    if owner_passphrase.strip() != OWNER_SECRET:
        st.error("Invalid owner passphrase.")
    else:
        new_key = generate_director_key()
        try:
            save_otp_to_analyser_config(new_key)
            st.success(f"New OTP generated and saved: `{new_key}`")
            st.info("The EduPulse-Analyzer will pick this up automatically on its next load.")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to save OTP: {exc}")