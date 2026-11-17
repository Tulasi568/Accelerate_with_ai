# Accelerate AI — Agentic Medallion Pipeline

A TDD-first implementation scaffold inspired by the Bronze → Silver → Gold architecture.

## Quickstart

```powershell
cd "c:\Users\ttulasijyothi\Downloads\accelerate_with_ai\IDAMP-20260915 2\accelarate_AI"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
streamlit run app\streamlit_app.py
```

## Current implementation status

This project is a working scaffold for an agentic medallion pipeline. It currently contains:

- configuration and environment validation
- audit logging and observability utilities
- profiling and STTM generation support
- Bronze, Silver, and Gold transformation functions
- a Streamlit UI for file upload and Phase 1 execution
- unit tests covering the core modules

It is not yet a complete end-to-end LLM-driven orchestration system matching the full reference architecture.

## Running tests

```powershell
.\venv\Scripts\python -m pytest -q
```

## Environment variables

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5
LLM_MAX_TOKENS=4096
```

## Project structure

```text
accelarate_AI/
├── agents/
│   ├── bronze_agent.py
│   ├── gold_agent.py
│   ├── orchestrator.py
│   ├── profiler.py
│   ├── reporter.py
│   ├── silver_agent.py
│   ├── sttm_generator.py
│   └── __init__.py
├── app/
│   └── streamlit_app.py
├── core/
│   ├── audit.py
│   ├── config.py
│   ├── memory.py
│   ├── observability.py
│   └── __init__.py
├── data/
├── tests/
├── .env.example
├── README.md
├── requirements.txt
└── ...
```

## Notes

The README in the parent folder describes the broader reference vision. This project README reflects the actual code in this repository: a tested, structured foundation that is ready for further extension, but not yet feature-complete relative to the full agentic pipeline design.

## Next steps

The next logical improvements are:

1. Connect the STTM generation to a real LLM provider
2. Complete the Bronze → Silver → Gold → Report orchestration flow
3. Add richer report generation with Plotly and SQL-backed analytics
4. Expand the front-end workflow beyond Phase 1

## Summary

This repository is a credible starting point for an agentic medallion pipeline and is suitable for continued development and learning, but it should be treated as a scaffold until the remaining orchestration and LLM integration steps are completed.
