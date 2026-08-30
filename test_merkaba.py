#!/usr/bin/env python3
"""
test_merkaba.py -- Automated test suite for Merkaba Ba/Ka generation, validation, and execution.
"""

import unittest
from pathlib import Path
import validator
import ka_gen
import ka_run

class TestMerkaba(unittest.TestCase):

    def test_ba_files_exist(self):
        ba_files = ["outclaw.ba.yaml", "truthsleuth.ba.yaml", "merkaba.ba.yaml", "bardildo.ba.yaml"]
        for bf in ba_files:
            self.assertTrue(Path(bf).exists(), f"{bf} missing")

    def test_validator_on_all_ba(self):
        ba_files = ["outclaw.ba.yaml", "truthsleuth.ba.yaml", "merkaba.ba.yaml", "bardildo.ba.yaml"]
        for bf in ba_files:
            self.assertTrue(validator.validate(Path(bf)), f"Validation failed for {bf}")

    def test_ka_validation_on_all_ka(self):
        ka_files = ["outclaw.ka.yaml", "truthsleuth.ka.yaml", "merkaba.ka.yaml", "bardildo.ka.yaml"]
        for kf in ka_files:
            ka_data = ka_gen.load_yaml(Path(kf))
            violations = ka_gen.validate_ka(ka_data)
            self.assertEqual(len(violations), 0, f"Ka violations in {kf}: {violations}")

    def test_signature_verification_and_tamper_detection(self):
        ka_files = ["outclaw.ka.yaml", "truthsleuth.ka.yaml", "merkaba.ka.yaml", "bardildo.ka.yaml"]
        for kf in ka_files:
            ka_data = ka_gen.load_yaml(Path(kf))
            self.assertTrue(ka_gen.verify_ka_signature(ka_data), f"Signature invalid for {kf}")

            # Tamper test
            tampered_ka = dict(ka_data)
            tampered_ka["ba_ref"] = "tampered_ref"
            self.assertFalse(ka_gen.verify_ka_signature(tampered_ka), f"Tamper detection failed for {kf}")

    def test_contract_execution_engine(self):
        ka_files = ["outclaw.ka.yaml", "truthsleuth.ka.yaml", "merkaba.ka.yaml", "bardildo.ka.yaml"]
        for kf in ka_files:
            receipt = ka_run.execute_ka(Path(kf))
            self.assertEqual(receipt.get("execution_status"), "COMPLETED", f"Execution failed for {kf}")
            self.assertIn("receipt_signature", receipt, f"Missing receipt signature for {kf}")
            self.assertEqual(len(receipt.get("execution_log", [])), 5, f"Expected 5 executed stages for {kf}")

    def test_ship_status(self):
        ba_files = ["outclaw.ba.yaml", "truthsleuth.ba.yaml", "merkaba.ba.yaml", "bardildo.ba.yaml"]
        for bf in ba_files:
            data = ka_gen.load_yaml(Path(bf))
            status = data.get("metadata", {}).get("status")
            self.assertEqual(status, "ship", f"Status in {bf} is {status}, expected 'ship'")

if __name__ == "__main__":
    unittest.main()
