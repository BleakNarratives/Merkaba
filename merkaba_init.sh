#!/usr/bin/env bash
# Merkaba bootstrap script
set -e

MERKABA_DIR="${HOME}/.merkaba"
mkdir -p "${MERKABA_DIR}/signed"

# Copy Root Ba declaration if present locally
if [ -f "root.ba.yaml" ]; then
    cp "root.ba.yaml" "${MERKABA_DIR}/root.ba.yaml"
    echo "Installed Root Ba axioms to ${MERKABA_DIR}/root.ba.yaml"
fi

# Copy system validator if present locally
if [ -f "validator.py" ]; then
    cp "validator.py" "${MERKABA_DIR}/validator.py"
    chmod +x "${MERKABA_DIR}/validator.py"
    echo "Installed Validator to ${MERKABA_DIR}/validator.py"
fi

# Copy execution engine if present locally
if [ -f "ka_run.py" ]; then
    cp "ka_run.py" "${MERKABA_DIR}/ka_run.py"
    chmod +x "${MERKABA_DIR}/ka_run.py"
    echo "Installed Execution Engine to ${MERKABA_DIR}/ka_run.py"
fi

echo "Merkaba runtime ready."
