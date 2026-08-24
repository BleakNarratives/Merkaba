# Merkaba

**Ba/Ka authoring system — agent contract generation and declaration.**

Merkaba defines the Ba (declarative state) and Ka (contractual behavior) system for agents. Every agent in the ecosystem has a Ba declaration (what it is) and a Ka contract (what it does). Merkaba generates and validates these contracts.

---

## Core Files

```
ka_gen.py               Ka contract generator
validator.py            Contract validator
merkaba_init.sh         Initialization script
```

## Ba Declarations

```yaml
root.ba.yaml            Root Ba — system-wide declaration
outclaw.ba.yaml         OutClaw Ba — accountability engine
truthsleuth.ba.yaml     TruthSleuth Ba — audit system (HOLD status)
```

## Ka Contracts

```yaml
outclaw.ka.json         OutClaw Ka — behavior contract
outclaw.ka.yaml         OutClaw Ka — YAML format
truthsleuth.ka.json     TruthSleuth Ka — behavior contract
```

## Purpose

- **Declarative identity** — every agent knows what it is
- **Contractual behavior** — every agent knows what it does
- **Signed contracts** — Ka contracts are signed and immutable
- **Validation** — ensures contracts are well-formed and consistent

## Usage

```bash
python ka_gen.py --help
```

---

*BleakNarratives // 2026*
