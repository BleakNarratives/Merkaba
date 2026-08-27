#!/usr/bin/env python3
"""
validator.py -- Incumbent/Repugnant root Ba validator.
Promoted from Man-Apart stub to system-wide validator.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[validator] PyYAML not installed. Install: pip install pyyaml")
    sys.exit(1)


def find_root_ba() -> Path:
    """Find root.ba.yaml in ~/.merkaba or local repo directory."""
    home_root = Path.home() / ".merkaba" / "root.ba.yaml"
    if home_root.exists():
        return home_root

    local_root = Path(__file__).parent / "root.ba.yaml"
    if local_root.exists():
        return local_root

    raise FileNotFoundError("root.ba.yaml not found in ~/.merkaba/ or local directory")


def validate_ba(data: dict, file_path: Path) -> list[str]:
    """Validate a Ba declaration against Root Ba axioms and schema."""
    violations = []
    
    # Required top-level Ba fields
    required_fields = ["name", "version", "intent", "success_criteria", "scope", "metadata"]
    for field in required_fields:
        if field not in data or not data[field]:
            violations.append(f"Ba missing required field or empty: '{field}'")

    # Scope check
    scope = data.get("scope", {})
    if isinstance(scope, dict):
        for s_field in ["in", "out", "boundaries"]:
            if s_field not in scope:
                violations.append(f"Ba scope missing field: '{s_field}'")
    else:
        violations.append("Ba scope must be a dictionary")

    # Metadata & ship_or_kill axiom check
    metadata = data.get("metadata", {})
    if isinstance(metadata, dict):
        status = metadata.get("status", "").lower()
        if not status:
            violations.append("Ba metadata missing 'status'")
        elif status not in ["ship", "kill"]:
            violations.append(f"SHIP_OR_KILL: Ba status is '{status}' — must resolve to 'ship' or 'kill'")
    else:
        violations.append("Ba metadata must be a dictionary")

    return violations


def validate(target_path: Path) -> bool:
    print(f"Validating {target_path}...")
    
    try:
        root_ba_path = find_root_ba()
        print(f"Using Root Ba: {root_ba_path}")
        with open(root_ba_path, "r", encoding="utf-8") as f:
            root_ba = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR loading root.ba.yaml: {e}")
        return False

    if not target_path.exists():
        print(f"ERROR: File not found: {target_path}")
        return False

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR parsing YAML in {target_path}: {e}")
        return False

    if not isinstance(data, dict):
        print(f"ERROR: Invalid YAML format in {target_path}")
        return False

    # Check if Ka or Ba file
    violations = []
    if "ka_version" in data or target_path.name.endswith(".ka.yaml"):
        # Import validate_ka from ka_gen if available
        try:
            from ka_gen import validate_ka
            violations = validate_ka(data)
        except ImportError:
            # Fallback basic Ka validation
            if data.get("metadata", {}).get("status") == "hold":
                violations.append("SHIP_OR_KILL: Ka status is HOLD — resolve to SHIP or KILL")
    else:
        violations = validate_ba(data, target_path)

    if violations:
        print(f"VALIDATION FAILED for {target_path.name} — {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        return False

    print(f"VALIDATION PASSED — {target_path.name} conforms to root axioms")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validator.py <ba_or_ka_file.yaml>")
        sys.exit(1)
    
    success = validate(Path(sys.argv[1]))
    sys.exit(0 if success else 1)
