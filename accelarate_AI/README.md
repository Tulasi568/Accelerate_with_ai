# Accelerate AI — Agentic Medallion Pipeline

A TDD-first implementation mirroring the reference project Bronze -> Silver -> Gold agentic architecture.

## Quickstart

cd "c:\Users\trekapalli\Downloads\accelerate_with_ai\IDAMP-20260915 2\accelarate_AI"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app\streamlit_app.py

## Running tests

pytest --cov=core --cov=agents --cov-report=term-missing

## Env vars

| Var | Purpose |
|---|---|
| LLM_PROVIDER | currently anthropic |
| ANTHROPIC_API_KEY | your Anthropic key - never commit this |
| ANTHROPIC_MODEL | e.g. claude-sonnet-4-5 |
| LLM_MAX_TOKENS | max tokens per LLM call |

## Structure

- core/ - config, audit logging, observability traces, memory/document store (fully unit tested).
- agents/ - profiler, bronze/silver/gold transformation logic (pure functions, LLM calls isolated/injectable), orchestrator.
- app/ - Streamlit UI entry point.
- data/ - bronze/silver/gold/sttm/profiles/reports/traces outputs (gitignored, dirs kept via .gitkeep).
- tests/ - hermetic unit tests, no network calls, >=80% coverage on core.

## Next steps

Wire agents/sttm_generator.py rule_builder to langchain_anthropic.ChatAnthropic
using core.config.get_settings() for credentials. Keep the LLM call injectable/mockable in tests.
