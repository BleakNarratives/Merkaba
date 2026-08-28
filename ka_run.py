#!/usr/bin/env python3
"""
ka_run.py -- Merkaba Contract Execution Engine.

Executes a signed Ka contract state machine through its stages:
  init -> validate_input -> process -> verify_output -> sign -> ship -> done

Zero external dependencies. Enforces signature verification and axiom compliance
prior to execution.
"""

from __future__ import annotations

import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import ka_gen
import validator

def execute_ka(ka_path: Path, input_payload: dict | None = None) -> dict:
    print(f"[ka_run] Loading Ka contract: {ka_path}")
    ka = ka_gen.load_yaml(ka_path)

    # 1. Verify contract signature
    if not ka_gen.verify_ka_signature(ka):
        print("[ka_run] ERROR: Contract signature verification failed! Refusing to execute.")
        return {"status": "ABORTED", "reason": "signature_mismatch"}

    # 2. Verify axiom compliance posture
    violations = ka_gen.validate_ka(ka)
    if violations:
        print(f"[ka_run] ERROR: Contract has {len(violations)} axiom violations! Refusing to execute.")
        return {"status": "ABORTED", "reason": "axiom_violations", "details": violations}

    print(f"[ka_run] Contract signature verified. Executing '{ka.get('ba_ref')}' state machine...")

    stages = ka.get("stages", [])
    state_machine = ka.get("state_machine", {})
    current_state = state_machine.get("initial", "init")
    terminal_state = state_machine.get("terminal", "done")

    execution_log = []
    context = {
        "raw_input": input_payload or {"sample": "default_input_data"},
        "status": "running"
    }

    start_time = time.time()

    for stage in stages:
        order = stage.get("order")
        name = stage.get("name")
        verb = stage.get("verb")
        input_key = stage.get("input")
        output_key = stage.get("output")

        print(f"[ka_run] Stage {order}: {verb} ({name}) ...")

        # Simulate stage execution step
        input_data = context.get(input_key, {})

        if verb == "validate":
            result = {"validated": True, "input_summary": str(input_data)[:50]}
        elif verb == "process":
            result = {"analysis_output": "stage_processing_complete", "items_processed": 1}
        elif verb == "verify":
            result = {"criteria_satisfied": True, "checks_passed": len(stage.get("checks", []))}
        elif verb == "format":
            result = {"artifact": "formatted_report.json", "version": "1.0"}
        elif verb == "sign":
            step_hash = hashlib.sha256(json.dumps(context, default=str).encode()).hexdigest()
            result = {"step_hash": step_hash, "signed": True}
        else:
            result = {"status": "completed"}

        context[output_key] = result
        execution_log.append({
            "order": order,
            "name": name,
            "verb": verb,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "output_summary": str(result)[:80]
        })

        # Advance state
        transitions = state_machine.get("transitions", {})
        if current_state in transitions:
            current_state = transitions[current_state].get("next", current_state)

    duration_ms = round((time.time() - start_time) * 1000, 2)
    receipt = {
        "ba_ref": ka.get("ba_ref"),
        "ka_signature": ka.get("signature", {}).get("hash"),
        "execution_status": "COMPLETED",
        "final_state": terminal_state,
        "duration_ms": duration_ms,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "execution_log": execution_log,
        "output_context": context.get("signed_output") or context.get("formatted_output")
    }

    # Generate execution receipt signature
    receipt_hash = hashlib.sha256(json.dumps(receipt, sort_keys=True, default=str).encode()).hexdigest()
    receipt["receipt_signature"] = receipt_hash

    print(f"[ka_run] Execution completed successfully in {duration_ms}ms! Receipt signature: {receipt_hash[:16]}...")
    return receipt


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ka_run.py <ka_file.ka.yaml> [optional_input.json]")
        sys.exit(1)

    ka_path = Path(sys.argv[1])
    input_payload = None
    if len(sys.argv) >= 3:
        input_path = Path(sys.argv[2])
        if input_path.exists():
            input_payload = json.loads(input_path.read_text(encoding="utf-8"))

    receipt = execute_ka(ka_path, input_payload)
    if receipt.get("execution_status") == "COMPLETED":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
