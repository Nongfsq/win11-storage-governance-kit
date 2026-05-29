# Replay Protocol

Use this protocol only for honest validation. Do not invent replay evidence.

## Dry-Run Replay

1. Pick a prompt from `examples/dry-runs.md`.
2. Invoke the skill with no local machine inspection unless the prompt explicitly asks for audit.
3. Check whether the answer:
   - Uses privacy-preserving placeholders.
   - Preserves do-not-touch rules.
   - Stages cleanup and migration.
   - Includes verification and rollback.

## Real Replay

Real replay requires an actual user session or machine audit. Record only anonymized findings unless the owner approves private recordkeeping.

## Evidence Labels

- `designed-dry-run`: expected behavior only.
- `forward-test`: independent agent test.
- `real-replay`: real user session evidence.

Never label a designed example as real replay.
