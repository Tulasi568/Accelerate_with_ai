# Accelerate AI – Project Status and Documentation

This repository is a working implementation scaffold for an agentic medallion data pipeline. It is intentionally designed to be TDD-first and to mirror the Bronze → Silver → Gold transformation model described in the reference architecture, while staying realistic about what is implemented today.

## Current status

The codebase is in a functional prototype state:

- Core configuration and directory setup are in place.
- Bronze, Silver, and Gold transformation logic is implemented as pure Python functions.
- STTM CSV generation is supported with an injectable rule builder.
- A Streamlit UI is present for CSV upload and Phase 1 execution.
- The project is covered by unit tests and currently passes.

This is not yet a fully autonomous production pipeline with live LLM orchestration across all pipeline stages.

## What is implemented

### Core platform
- Centralized configuration via environment variables in [core/config.py](./accelarate_AI/core/config.py)
- Audit logging and observability scaffolding in [core/audit.py](./accelarate_AI/core/audit.py) and [core/observability.py](./accelarate_AI/core/observability.py)
- In-memory document/memory utilities in [core/memory.py](./accelarate_AI/core/memory.py)

### Agent modules
- [agents/profiler.py](./accelarate_AI/agents/profiler.py)
- [agents/bronze_agent.py](./accelarate_AI/agents/bronze_agent.py)
- [agents/silver_agent.py](./accelarate_AI/agents/silver_agent.py)
- [agents/gold_agent.py](./accelarate_AI/agents/gold_agent.py)
- [agents/reporter.py](./accelarate_AI/agents/reporter.py)
- [agents/sttm_generator.py](./accelarate_AI/agents/sttm_generator.py)
- [agents/orchestrator.py](./accelarate_AI/agents/orchestrator.py)

### Application layer
- A Streamlit entry point is available at [app/streamlit_app.py](./accelarate_AI/app/streamlit_app.py)
- It supports uploading raw CSV files and running the initial profiling + Bronze STTM generation flow.

### Data model and output flow
- Bronze: CSV → parquet + metadata injection
- Silver: Bronze cleansing + null handling + surrogate key injection
- Gold: structured join/aggregation output
- Reporter: minimal HTML report generation using DuckDB and JSON payloads

## What is not yet complete

The following items are intentionally not yet wired to the full end-to-end reference implementation:

- Live Anthropic/LLM-based STTM generation via langchain_anthropic
- Full orchestration of all phases from the UI
- Human approval gates across Bronze/Silver/Gold steps
- Advanced Plotly chart generation for a rich executive report
- Production-grade agent loop behavior across all stages

The project is best described as a solid scaffold and working foundation for the full architecture described in the reference design.

## Quickstart

From the project directory:

```powershell
cd "c:\Users\ttulasijyothi\Downloads\accelerate_with_ai\IDAMP-20260915 2\accelarate_AI"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
streamlit run app\streamlit_app.py
```

## Environment variables

Create a `.env` file using `.env.example`.

Required example values:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5
LLM_MAX_TOKENS=4096
```

Notes:
- The project is configured to validate that the Anthropic key is present before the UI starts.
- LLM integration is prepared structurally but not yet fully wired into the runtime path.

## Testing

Run the suite with:

```powershell
.\venv\Scripts\python -m pytest -q
```

Current status: the test suite passes.

## Project structure

```text
accelarate_AI/
├── agents/
├── app/
├── core/
├── data/
├── tests/
├── .env.example
├── README.md
├── requirements.txt
└── ...
```

## Recommended next steps

1. Wire the actual LLM call in [agents/sttm_generator.py](./accelarate_AI/agents/sttm_generator.py)
2. Complete the end-to-end orchestration flow in [agents/orchestrator.py](./accelarate_AI/agents/orchestrator.py)
3. Add UI progression through Bronze → Silver → Gold → report
4. Replace the minimal reporter with richer analytics output
5. Expand tests for the full pipeline lifecycle

## Summary

This repository is a credible implementation foundation for an agentic data engineering workflow. It is organized, tested, and workable as a scaffold, but it should be documented as such rather than as a fully production-complete medallion pipeline.
