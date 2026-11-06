"""Supervisor orchestrator: wires phases together via PipelineState."""
from __future__ import annotations

import uuid
from typing import TypedDict

from core.audit import AuditLogger
from core.config import TRACES_DIR
from agents import profiler, bronze_agent, silver_agent, gold_agent


class PipelineState(TypedDict, total=False):
    run_id: str
    business_intent: str
    input_files: list[str]
    profile_path: str
    bronze_sttm_path: str
    bronze_files: list[str]
    silver_sttm_path: str
    silver_files: list[str]
    gold_sttm_path: str
    gold_files: list[str]
    report_path: str


def run_until_bronze_sttm(
    input_files: list[str], business_intent: str, sttm_path: str
) -> PipelineState:
    """Phase 1: Profiler -> (human reviews/approves pre-generated Bronze STTM)."""
    run_id = str(uuid.uuid4())
    audit = AuditLogger(log_dir=TRACES_DIR)
    audit.log(run_id, "profile", "start")
    profile_path = profiler.profile_multiple_datasets(input_files, run_id=run_id)
    audit.log(run_id, "profile", "complete", {"profile_path": profile_path})
    return PipelineState(
        run_id=run_id,
        business_intent=business_intent,
        input_files=input_files,
        profile_path=profile_path,
        bronze_sttm_path=sttm_path,
    )


def run_bronze(state: PipelineState) -> PipelineState:
    """Phase 2: ingest Bronze using the human-approved STTM."""
    audit = AuditLogger(log_dir=TRACES_DIR)
    audit.log(state["run_id"], "bronze", "start")
    bronze_files = bronze_agent.apply_bronze_rules(
        state["input_files"], state["bronze_sttm_path"], state["run_id"]
    )
    audit.log(state["run_id"], "bronze", "complete", {"files": bronze_files})
    return {**state, "bronze_files": bronze_files}


def run_silver(state: PipelineState, silver_sttm_path: str) -> PipelineState:
    """Phase 3: cleanse Silver using the human-approved STTM."""
    audit = AuditLogger(log_dir=TRACES_DIR)
    audit.log(state["run_id"], "silver", "start")
    silver_files = silver_agent.apply_silver_rules(
        state["bronze_files"], silver_sttm_path, state["run_id"]
    )
    audit.log(state["run_id"], "silver", "complete", {"files": silver_files})
    return {**state, "silver_sttm_path": silver_sttm_path, "silver_files": silver_files}


def run_gold(state: PipelineState, gold_sttm_path: str) -> PipelineState:
    """Phase 4: materialise Gold using the human-approved STTM."""
    audit = AuditLogger(log_dir=TRACES_DIR)
    audit.log(state["run_id"], "gold", "start")
    gold_files = gold_agent.apply_gold_rules(
        state["silver_files"], gold_sttm_path, state["run_id"]
    )
    audit.log(state["run_id"], "gold", "complete", {"files": gold_files})
    return {**state, "gold_sttm_path": gold_sttm_path, "gold_files": gold_files}
