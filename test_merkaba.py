#!/usr/bin/env python3
"""
test_merkaba.py -- Test suite for Merkaba repository health and validation.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path
import yaml


class TestMerkabaRepositoryHealth(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).parent

    def test_validator_on_all_ba_files(self):
        ba_files = list(self.repo_root.glob("*.ba.yaml"))
        self.assertTrue(len(ba_files) > 0, "No Ba files found in repo root")

        for ba_file in ba_files:
            if ba_file.name == "root.ba.yaml":
                continue
            res = subprocess.run(
                [sys.executable, "validator.py", str(ba_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res.returncode,
                0,
                f"Validation failed for {ba_file.name}:\n{res.stdout}\n{res.stderr}",
            )

    def test_validator_on_all_ka_files(self):
        ka_files = list(self.repo_root.glob("*.ka.yaml"))
        self.assertTrue(len(ka_files) > 0, "No Ka files found in repo root")

        for ka_file in ka_files:
            res = subprocess.run(
                [sys.executable, "validator.py", str(ka_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res.returncode,
                0,
                f"Validation failed for {ka_file.name}:\n{res.stdout}\n{res.stderr}",
            )

    def test_signed_contracts_in_sync(self):
        ka_files = list(self.repo_root.glob("*.ka.yaml"))
        for ka_file in ka_files:
            signed_file = self.repo_root / "signed" / ka_file.name
            self.assertTrue(
                signed_file.exists(),
                f"Signed copy missing for {ka_file.name} in signed/",
            )

            with open(ka_file, "r") as f:
                ka_data = yaml.safe_load(f)
            with open(signed_file, "r") as f:
                signed_data = yaml.safe_load(f)

            self.assertEqual(
                ka_data.get("signature", {}).get("hash"),
                signed_data.get("signature", {}).get("hash"),
                f"Signature mismatch between {ka_file.name} and signed/{signed_file.name}",
            )

    def test_merkaba_init_script(self):
        res = subprocess.run(["bash", "merkaba_init.sh"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"merkaba_init.sh failed: {res.stderr}")
        home_merkaba = Path.home() / ".merkaba"
        self.assertTrue((home_merkaba / "root.ba.yaml").exists())
        self.assertTrue((home_merkaba / "validator.py").exists())


if __name__ == "__main__":
    unittest.main()
