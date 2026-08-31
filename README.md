# Merkaba

**Ba/Ka authoring system — agent contract generation, declaration, and execution engine.**

Merkaba defines the Ba (declarative state) and Ka (contractual behavior) system for agents. Every agent in the ecosystem has a Ba declaration (what it is) and a Ka contract (what it does). Merkaba generates, validates, signs, and executes these contracts with zero external dependencies.

---

## Core Infrastructure & Tools

```
ka_gen.py               Ka contract generator & signature verifier
validator.py            Root Ba axiom compliance validator
ka_run.py               Ka contract execution engine
merkaba_init.sh         System bootstrapping & environment initialization
test_merkaba.py         Comprehensive automated test suite
test_red_team.py        Red Team adversarial security test suite
```

## Ba Declarations

```yaml
root.ba.yaml            Root Ba — system-wide declaration & 8 Root Axioms
outclaw.ba.yaml         OutClaw Ba — accountability engine (SHIP status)
truthsleuth.ba.yaml     TruthSleuth Ba — audit rhetoric analyzer (SHIP status)
merkaba.ba.yaml         Merkaba Ba — unified Ka+Ba synthesis agent (SHIP status)
```

## Ka Contracts & Execution Receipts

```yaml
outclaw.ka.yaml         OutClaw Ka — behavior contract (.json sidecar included)
truthsleuth.ka.yaml     TruthSleuth Ka — behavior contract (.json sidecar included)
merkaba.ka.yaml         Merkaba Ka — behavior contract (.json sidecar included)
```

## Core Principles & Root Axioms

- **Declarative Identity (Ba)** — Every agent knows what it is.
- **Contractual Behavior (Ka)** — Every agent knows what it does.
- **Cryptographic Signatures** — All Ka contracts are SHA-256 signed upon generation.
- **Zero-Dependency Execution** — Pure-Python YAML parsing, contract verification, and state machine execution with no mandatory external server sockets or packages.
- **Axiom Compliance** — Enforces all 8 Root Ba Axioms: `no_orphan_code`, `no_larp`, `no_pokemon_skills`, `no_eternal_defer`, `no_print_theater`, `ka_must_earn_ba`, `scope_is_law`, and `ship_or_kill`.

## Usage

```bash
# 1. Initialize environment
./merkaba_init.sh

# 2. Validate Ba declaration against Root Axioms
python3 validator.py merkaba.ba.yaml

# 3. Generate SHA-256 signed Ka contract
python3 ka_gen.py merkaba.ba.yaml

# 4. Verify contract signature integrity
python3 ka_gen.py --verify-sig merkaba.ka.yaml

# 5. Execute contract state machine
python3 ka_run.py merkaba.ka.yaml

# 6. Run test suites
python3 test_merkaba.py
python3 test_red_team.py
```

---

*BleakNarratives // 2026*
