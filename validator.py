#!/usr/bin/env python3
"""
validator.py -- Incumbent/Repugnant root Ba validator.
Promoted from Man-Apart stub to system-wide validator.
Zero external dependencies.
"""

import sys
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

def parse_yaml_minimal(content: str) -> dict:
    """Pure-Python minimal YAML parser for Ba/Ka files when PyYAML is not installed."""
    if yaml is not None:
        return yaml.safe_load(content)

    lines = content.splitlines()
    data = {}
    current_section = None
    current_key = None
    in_block_scalar = False
    block_lines = []
    block_indent = 0

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith('#'):
            continue

        indent = len(raw_line) - len(raw_line.lstrip())

        if in_block_scalar:
            if indent > block_indent or not raw_line.strip():
                block_lines.append(raw_line.strip())
                continue
            else:
                if current_section and current_key:
                    data.setdefault(current_section, {})[current_key] = "\n".join(block_lines)
                elif current_key:
                    data[current_key] = "\n".join(block_lines)
                in_block_scalar = False
                block_lines = []

        stripped = line.strip()

        # Check section header (indent == 0)
        if indent == 0 and ':' in stripped and not stripped.startswith('-'):
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"\'').strip()

            if val == '|':
                in_block_scalar = True
                block_indent = indent
                current_section = None
                current_key = key
                block_lines = []
                continue

            if val:
                data[key] = val
                current_section = None
                current_key = key
            else:
                current_section = key
                data.setdefault(current_section, {})
                current_key = None
            continue

        # Nested keys (indent > 0)
        if current_section and ':' in stripped and not stripped.startswith('-'):
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"\'').strip()

            if val == '|':
                in_block_scalar = True
                block_indent = indent
                current_key = key
                block_lines = []
                continue

            if val.startswith('[') and val.endswith(']'):
                items = [x.strip().strip('"\'').strip() for x in val[1:-1].split(',') if x.strip()]
                data[current_section][key] = items
            elif val:
                data[current_section][key] = val
            else:
                data[current_section].setdefault(key, {})
            current_key = key
            continue

        # List items
        if stripped.startswith('- '):
            item = stripped[2:].strip().strip('"\'').strip()
            if current_section and current_key:
                sec_dict = data[current_section]
                if not isinstance(sec_dict.get(current_key), list):
                    sec_dict[current_key] = []
                sec_dict[current_key].append(item)
            elif current_section:
                if not isinstance(data[current_section], list):
                    data[current_section] = []
                data[current_section].append(item)
            elif current_key:
                if not isinstance(data.get(current_key), list):
                    data[current_key] = []
                data[current_key].append(item)

    if in_block_scalar and current_key:
        if current_section:
            data.setdefault(current_section, {})[current_key] = "\n".join(block_lines)
        else:
            data[current_key] = "\n".join(block_lines)

    return data


def load_yaml(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if yaml is not None:
        return yaml.safe_load(content)
    try:
        return json.loads(content)
    except Exception:
        return parse_yaml_minimal(content)


def find_root_ba() -> dict:
    local_root = Path("root.ba.yaml")
    home_root = Path.home() / ".merkaba" / "root.ba.yaml"

    if local_root.exists():
        return load_yaml(local_root)
    elif home_root.exists():
        return load_yaml(home_root)
    else:
        return {
            "axioms": [
                "no_orphan_code",
                "no_larp",
                "no_pokemon_skills",
                "no_eternal_defer",
                "no_print_theater",
                "ka_must_earn_ba",
                "scope_is_law",
                "ship_or_kill",
            ]
        }


def validate(ba_path: Path) -> bool:
    print(f"Validating {ba_path}...")
    if not ba_path.exists():
        print(f"ERROR: File not found: {ba_path}")
        return False

    root_ba = find_root_ba()
    axioms = root_ba.get("axioms", [
        "no_orphan_code",
        "no_larp",
        "no_pokemon_skills",
        "no_eternal_defer",
        "no_print_theater",
        "ka_must_earn_ba",
        "scope_is_law",
        "ship_or_kill",
    ])

    data = load_yaml(ba_path)

    if not isinstance(data, dict):
        print(f"ERROR: {ba_path} is not a valid Ba declaration")
        return False

    violations = []

    # 1. ship_or_kill
    if "ship_or_kill" in axioms:
        metadata = data.get("metadata", {})
        status = ""
        if isinstance(metadata, dict):
            status = str(metadata.get("status", "")).strip().strip('"\'').strip().lower()

        if status == "hold":
            violations.append("SHIP_OR_KILL violation: status is 'hold' (must resolve to 'ship' or 'kill')")

    # 2. scope_is_law
    if "scope_is_law" in axioms:
        scope = data.get("scope", {})
        if not isinstance(scope, dict) or "in" not in scope or "out" not in scope:
            violations.append("SCOPE_IS_LAW violation: scope must specify both 'in' and 'out'")

    # 3. ka_must_earn_ba
    if "ka_must_earn_ba" in axioms:
        criteria = data.get("success_criteria", [])
        if not criteria or not isinstance(criteria, list):
            violations.append("KA_MUST_EARN_BA violation: success_criteria must be a non-empty list")

    # 4. no_larp
    if "no_larp" in axioms:
        intent = str(data.get("intent", "")).strip()
        name = str(data.get("name", "")).strip()
        if not intent or not name:
            violations.append("NO_LARP violation: Ba declaration must have non-empty name and intent")

    # 5. no_pokemon_skills
    if "no_pokemon_skills" in axioms:
        requires = data.get("requires", [])
        if any("catch_all" in str(r).lower() or "*" in str(r) for r in requires):
            violations.append("NO_POKEMON_SKILLS violation: wildcards or catch-all dependencies forbidden")

    # 6. no_orphan_code
    if "no_orphan_code" in axioms:
        scope_in = data.get("scope", {}).get("in", [])
        if not scope_in:
            violations.append("NO_ORPHAN_CODE violation: scope.in cannot be empty")

    # 7. no_print_theater
    if "no_print_theater" in axioms:
        intent = str(data.get("intent", "")).lower()
        if "mock_only" in intent or "print_only" in intent:
            violations.append("NO_PRINT_THEATER violation: fake or mock-only intent detected")

    # 8. no_eternal_defer
    if "no_eternal_defer" in axioms:
        if data.get("metadata", {}).get("defer_count", 0) > 3:
            violations.append("NO_ETERNAL_DEFER violation: task deferred more than 3 times")

    if violations:
        print(f"VALIDATION FAILED ({len(violations)} violations):")
        for v in violations:
            print(f"  - {v}")
        return False

    print("VALIDATION PASSED — Ba conforms to all Root Ba Axioms")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validator.py <ba_file.yaml>")
        sys.exit(1)

    if validate(Path(sys.argv[1])):
        sys.exit(0)
    else:
        sys.exit(1)
