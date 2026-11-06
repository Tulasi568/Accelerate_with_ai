"""Streamlit UI — entry point for users (upload CSVs, ask question, approve STTM)."""
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from agents import orchestrator
from core.config import ensure_data_dirs, get_settings

RAW_DIR = Path("data/raw")
STTM_DIR = Path("data/sttm")


def save_uploaded_files(uploaded_files) -> list[str]:
    """Persist uploaded files to the raw data directory and return their paths."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for uploaded_file in uploaded_files:
        dest = RAW_DIR / uploaded_file.name
        dest.write_bytes(uploaded_file.getbuffer())
        saved_paths.append(str(dest))
    return saved_paths


def run_phase1(input_files: list[str], business_intent: str) -> dict:
    """Run profiling + Bronze STTM generation. Raises ValueError on invalid input."""
    if not input_files:
        raise ValueError("Please upload at least one CSV file.")
    if not business_intent or not business_intent.strip():
        raise ValueError("Please enter a business question.")

    STTM_DIR.mkdir(parents=True, exist_ok=True)
    sttm_path = str(STTM_DIR / f"sttm_bronze_{uuid.uuid4().hex[:8]}.csv")

    return orchestrator.run_until_bronze_sttm(
        input_files=input_files,
        business_intent=business_intent,
        sttm_path=sttm_path,
    )


st.set_page_config(page_title="Accelerate AI — Medallion Pipeline", layout="wide")
ensure_data_dirs()

settings = get_settings()

st.title("Accelerate AI — Agentic Medallion Pipeline")

try:
    settings.validate()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.success(f"LLM provider: {settings.llm_provider} | model: {settings.anthropic_model}")

uploaded_files = st.file_uploader("Upload raw CSV files", type="csv", accept_multiple_files=True)
business_intent = st.text_input("Business question", placeholder="e.g. Which category had the highest sales?")

if st.button("Run Phase 1 — Profile & Generate Bronze STTM"):
    try:
        saved_paths = save_uploaded_files(uploaded_files or [])
        state = run_phase1(saved_paths, business_intent)
        st.success(f"Run {state['run_id']} complete. Profile saved to {state['profile_path']}.")
        st.session_state["phase1_state"] = state
    except ValueError as exc:
        st.warning(str(exc))
