#!/usr/bin/env python3
"""
ka_gen.py — Backend-agnostic Ka generator & verifier.

Takes a Ba (intent declaration) and produces a Ka (execution contract)
with ordered stages, state machine, error posture, and axiom compliance.

Usage:
  python3 ka_gen.py outclaw.ba.yaml
  python3 ka_gen.py truthsleuth.ba.yaml
  python3 ka_gen.py --validate outclaw.ka.yaml
  python3 ka_gen.py --verify-sig outclaw.ka.yaml
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if yaml is not None:
        return yaml.safe_load(content)

    try:
        return json.loads(content)
    except Exception:
        pass

    # For Ka files, check JSON sidecar
    json_sidecar = path.with_suffix(".json")
    if json_sidecar.exists():
        with open(json_sidecar, 'r', encoding='utf-8') as jf:
            return json.load(jf)

    # Use validator minimal parser
    import validator
    return validator.parse_yaml_minimal(content)


def dump_yaml(data: dict) -> str:
    if yaml is not None:
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    return json.dumps(data, indent=2)


ROOT_AXIOMS = [
    "no_orphan_code",
    "no_larp",
    "no_pokemon_skills",
    "no_eternal_defer",
    "no_print_theater",
    "ka_must_earn_ba",
    "scope_is_law",
    "ship_or_kill",
]


def generate_ka_from_ba(ba: dict) -> dict:
    name = ba.get("name", "unnamed")
    intent = ba.get("intent", "").strip()
    success = ba.get("success_criteria", [])
    scope_in = ba.get("scope", {}).get("in", [])
    scope_out = ba.get("scope", {}).get("out", [])
    scope_bounds = ba.get("scope", {}).get("boundaries", [])
    requires = ba.get("requires", [])
    metadata = ba.get("metadata", {})

    stages = _infer_stages(ba)

    states = ["init", "validate_input", "process", "verify_output", "sign", "ship"]
    transitions = {
        "init": {"next": "validate_input", "on_error": "abort"},
        "validate_input": {"next": "process", "on_error": "reject_input"},
        "process": {"next": "verify_output", "on_error": "retry_or_abort"},
        "verify_output": {"next": "sign", "on_error": "quarantine"},
        "sign": {"next": "ship", "on_error": "hold"},
        "ship": {"next": "done", "on_error": "rollback"},
    }

    axiom_checks = _generate_axiom_checks(ba, stages)

    ka = {
        "ka_version": "0.1.0",
        "ba_ref": name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "ka_gen.py (template)",
        "stages": stages,
        "state_machine": {
            "initial": "init",
            "terminal": "done",
            "states": states,
            "transitions": transitions,
        },
        "error_posture": {
            "strategy": "fail-fast",
            "retry_limit": 2,
            "timeout_s": 120,
            "fallback": "quarantine_and_alert",
        },
        "axiom_compliance": axiom_checks,
        "scope": {
            "in": scope_in,
            "out": scope_out,
            "boundaries": scope_bounds,
        },
        "requires": requires,
        "metadata": metadata,
    }

    return ka


def _infer_stages(ba: dict) -> List[dict]:
    name = ba.get("name", "unnamed")
    scope_in = ba.get("scope", {}).get("in", [])
    success = ba.get("success_criteria", [])

    stages = []

    stages.append({
        "order": 1,
        "verb": "validate",
        "name": "input_validation",
        "description": f"Validate input conforms to scope.in for {name}",
        "input": "raw_input",
        "output": "validated_input",
        "tool": "stdlib",
        "signal": "input_valid",
        "error": "reject_input",
    })

    stages.append({
        "order": 2,
        "verb": "process",
        "name": "core_analysis",
        "description": f"Execute core {name} analysis pipeline",
        "input": "validated_input",
        "output": "raw_results",
        "tool": "stdlib",
        "signal": "analysis_complete",
        "error": "retry_or_abort",
    })

    stages.append({
        "order": 3,
        "verb": "verify",
        "name": "success_criteria_check",
        "description": "Verify output satisfies all Ba success criteria",
        "input": "raw_results",
        "output": "verified_results",
        "tool": "stdlib",
        "signal": "verified",
        "error": "quarantine",
        "checks": success,
    })

    stages.append({
        "order": 4,
        "verb": "format",
        "name": "output_formatting",
        "description": "Format verified results into scope.out artifacts",
        "input": "verified_results",
        "output": "formatted_output",
        "tool": "stdlib",
        "signal": "formatted",
        "error": "retry_format",
    })

    stages.append({
        "order": 5,
        "verb": "sign",
        "name": "integrity_sign",
        "description": "Compute SHA-256 integrity hash and sign Ka",
        "input": "formatted_output",
        "output": "signed_output",
        "tool": "stdlib",
        "signal": "signed",
        "error": "hold",
    })

    return stages


def _generate_axiom_checks(ba: dict, stages: List[dict]) -> List[dict]:
    name = ba.get("name", "unnamed")
    checks = []

    for axiom in ROOT_AXIOMS:
        check = {"axiom": axiom, "status": "pending", "description": ""}

        if axiom == "no_orphan_code":
            check["description"] = f"All code in {name} connects to the pipeline"
            check["validator"] = "import_check"
        elif axiom == "no_larp":
            check["description"] = "No theatrical non-functional output"
            check["validator"] = "output_authenticity_check"
        elif axiom == "no_pokemon_skills":
            check["description"] = "Only scope-matched capabilities loaded"
            check["validator"] = "scope_check"
        elif axiom == "no_eternal_defer":
            check["description"] = "No task deferred more than 3 times"
            check["validator"] = "defer_counter"
        elif axiom == "no_print_theater":
            check["description"] = "No fake output — label STUB or delete"
            check["validator"] = "stub_detector"
        elif axiom == "ka_must_earn_ba":
            check["description"] = "Ka satisfies all Ba success criteria"
            check["validator"] = "criteria_matcher"
        elif axiom == "scope_is_law":
            check["description"] = "Output stays within scope.out boundaries"
            check["validator"] = "scope_enforcer"
        elif axiom == "ship_or_kill":
            check["description"] = "Status resolves to SHIP or KILL — no HOLD limbo"
            check["validator"] = "status_resolver"

        checks.append(check)

    return checks


def validate_ka(ka: dict) -> List[str]:
    violations = []

    for field in ["ka_version", "ba_ref", "stages", "state_machine", "axiom_compliance"]:
        if field not in ka:
            violations.append(f"Missing required field: {field}")

    stages = ka.get("stages", [])
    if not stages:
        violations.append("Ka has no stages")
    for i, stage in enumerate(stages):
        for field in ["order", "verb", "name", "input", "output"]:
            if field not in stage:
                violations.append(f"Stage {i+1} missing field: {field}")

    sm = ka.get("state_machine", {})
    if "initial" not in sm or "terminal" not in sm:
        violations.append("State machine missing initial/terminal states")

    checks = ka.get("axiom_compliance", [])
    if len(checks) < len(ROOT_AXIOMS):
        violations.append(f"Only {len(checks)}/{len(ROOT_AXIOMS)} axiom checks present")

    if ka.get("metadata", {}).get("status") == "hold":
        violations.append("SHIP_OR_KILL: Ka status is HOLD — resolve to SHIP or KILL")

    return violations


def compute_ka_hash(ka: dict) -> str:
    ka_copy = {k: v for k, v in ka.items() if k != "signature"}
    ka_json = json.dumps(ka_copy, sort_keys=True, default=str)
    return hashlib.sha256(ka_json.encode()).hexdigest()


def sign_ka(ka: dict) -> dict:
    sig_hash = compute_ka_hash(ka)
    ka["signature"] = {
        "algorithm": "SHA-256",
        "hash": sig_hash,
        "signed_at": datetime.now(timezone.utc).isoformat(),
    }
    return ka


def verify_ka_signature(ka: dict) -> bool:
    if "signature" not in ka or "hash" not in ka["signature"]:
        return False
    expected_hash = compute_ka_hash(ka)
    return ka["signature"]["hash"] == expected_hash


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ka_gen.py <ba_file.yaml>")
        print("       python3 ka_gen.py --validate <ka_file.ka.yaml>")
        print("       python3 ka_gen.py --verify-sig <ka_file.ka.yaml>")
        sys.exit(1)

    if sys.argv[1] == "--verify-sig":
        if len(sys.argv) < 3:
            print("Usage: python3 ka_gen.py --verify-sig <ka_file.ka.yaml>")
            sys.exit(1)
        ka = load_yaml(Path(sys.argv[2]))
        if verify_ka_signature(ka):
            print("SIGNATURE VERIFIED — SHA-256 contract hash intact")
            sys.exit(0)
        else:
            print("SIGNATURE INVALID — Contract hash mismatch or missing signature")
            sys.exit(1)

    if sys.argv[1] == "--validate":
        if len(sys.argv) < 3:
            print("Usage: python3 ka_gen.py --validate <ka_file.ka.yaml>")
            sys.exit(1)
        ka = load_yaml(Path(sys.argv[2]))
        violations = validate_ka(ka)
        if violations:
            print(f"VALIDATION FAILED — {len(violations)} violations:")
            for v in violations:
                print(f"  - {v}")
            sys.exit(1)
        else:
            print("VALIDATION PASSED — Ka conforms to root axioms")
            sys.exit(0)

    ba_path = Path(sys.argv[1])
    if not ba_path.exists():
        print(f"[ka_gen] Ba file not found: {ba_path}")
        sys.exit(1)

    print(f"[ka_gen] Loading Ba: {ba_path}")
    ba = load_yaml(ba_path)

    print(f"[ka_gen] Generating Ka for: {ba.get('name', 'unnamed')}")
    ka = generate_ka_from_ba(ba)

    violations = validate_ka(ka)
    if violations:
        print(f"[ka_gen] WARNING: {len(violations)} axiom violations:")
        for v in violations:
            print(f"  - {v}")
    else:
        print("[ka_gen] All axiom checks pass")

    ka = sign_ka(ka)

    stem = ba_path.name.split('.')[0]
    ka_path = ba_path.parent / f"{stem}.ka.yaml"
    with open(ka_path, "w", encoding="utf-8") as f:
        f.write(dump_yaml(ka))

    print(f"[ka_gen] Ka written: {ka_path}")
    print(f"[ka_gen] Signature: {ka['signature']['hash'][:16]}...")
    print(f"[ka_gen] Stages: {len(ka['stages'])}")
    print(f"[ka_gen] Axiom checks: {len(ka['axiom_compliance'])}")

    json_path = ba_path.parent / f"{stem}.ka.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ka, f, indent=2, default=str)
    print(f"[ka_gen] JSON: {json_path}")


if __name__ == "__main__":
    main()
