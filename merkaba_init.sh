#!/usr/bin/env bash
# Merkaba bootstrap script
set -e

MERKABA_DIR="$HOME/.merkaba"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$MERKABA_DIR/signed"

if [ -f "$SCRIPT_DIR/root.ba.yaml" ]; then
    cp "$SCRIPT_DIR/root.ba.yaml" "$MERKABA_DIR/root.ba.yaml"
fi

if [ -f "$SCRIPT_DIR/validator.py" ]; then
    cp "$SCRIPT_DIR/validator.py" "$MERKABA_DIR/validator.py"
fi

echo "Merkaba runtime ready at $MERKABA_DIR."
