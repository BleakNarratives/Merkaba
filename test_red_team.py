#!/usr/bin/env python3
"""
test_red_team.py -- Red Team Adversarial Test Suite for Merkaba.
Tests signature forgery, schema evasion, status injection, parser differentials,
and scope boundary bypasses.
"""

import unittest
import tempfile
from pathlib import Path
import validator
import ka_gen

class TestMerkabaRedTeam(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_red_team_status_comment_injection(self):
        """Attacker attempts to hide status: hold inside a comment while metadata says status: ship."""
        payload = """
name: spoof-agent
version: "1.0.0"
intent: Clean intent
success_criteria:
  - Valid criteria
scope:
  in:
    - input_data
  out:
    - output_data
# metadata:
#   status: hold
metadata:
  status: ship
"""
        ba_file = self.temp_path / "spoof.ba.yaml"
        ba_file.write_text(payload, encoding="utf-8")
        self.assertTrue(validator.validate(ba_file), "Valid status: ship was incorrectly rejected due to comment")

    def test_red_team_hold_status_evasion(self):
        """Attacker tries case variation or whitespace to evade hold status check."""
        payloads = [
            "metadata:\n  status: HOLD",
            "metadata:\n  status: '  hold  '",
            "metadata:\n  status: HoLd",
        ]
        for i, p in enumerate(payloads):
            full_payload = f"""
name: hold-evasion-{i}
version: "1.0.0"
intent: Clean intent
success_criteria:
  - Valid criteria
scope:
  in: [input]
  out: [output]
{p}
"""
            ba_file = self.temp_path / f"hold_evasion_{i}.ba.yaml"
            ba_file.write_text(full_payload, encoding="utf-8")
            self.assertFalse(validator.validate(ba_file), f"Failed to catch hold status evasion in payload {i}")

    def test_red_team_ka_signature_tampering(self):
        """Attacker modifies stage details or error posture in signed Ka."""
        ba_file = Path("merkaba.ba.yaml")
        ka = ka_gen.generate_ka_from_ba(validator.load_yaml(ba_file))
        signed_ka = ka_gen.sign_ka(ka)

        # Confirm valid signature
        self.assertTrue(ka_gen.verify_ka_signature(signed_ka))

        # Tamper stage tool
        tampered_ka = json_copy(signed_ka)
        tampered_ka["stages"][0]["tool"] = "malicious_tool"
        self.assertFalse(ka_gen.verify_ka_signature(tampered_ka), "Tampered stage tool went undetected")

        # Tamper error posture
        tampered_ka2 = json_copy(signed_ka)
        tampered_ka2["error_posture"]["strategy"] = "ignore-errors"
        self.assertFalse(ka_gen.verify_ka_signature(tampered_ka2), "Tampered error posture went undetected")

    def test_red_team_pokemon_skills_wildcard_bypass(self):
        """Attacker attempts to sneak wildcard dependencies into requires."""
        payload = """
name: wildcard-agent
version: "1.0.0"
intent: Clean intent
success_criteria:
  - Valid criteria
scope:
  in: [input]
  out: [output]
requires:
  - "all_skills_*"
metadata:
  status: ship
"""
        ba_file = self.temp_path / "wildcard.ba.yaml"
        ba_file.write_text(payload, encoding="utf-8")
        self.assertFalse(validator.validate(ba_file), "Failed to detect wildcard skill dependency")

    def test_red_team_empty_scope_in_evasion(self):
        """Attacker passes empty scope in list."""
        payload = """
name: empty-scope-agent
version: "1.0.0"
intent: Clean intent
success_criteria:
  - Valid criteria
scope:
  in: []
  out: [output]
metadata:
  status: ship
"""
        ba_file = self.temp_path / "empty_scope.ba.yaml"
        ba_file.write_text(payload, encoding="utf-8")
        self.assertFalse(validator.validate(ba_file), "Failed to detect empty scope.in")

def json_copy(d):
    import json
    return json.loads(json.dumps(d, default=str))

if __name__ == "__main__":
    unittest.main()
