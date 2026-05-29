# Project Rules

This repository is a reusable Windows 11 storage governance kit.

## Privacy

- Do not add real usernames, emails, machine names, private project paths, package inventories, shell history, logs, tokens, or environment variable dumps.
- Keep examples anonymized with placeholders.
- Treat the included drive layout as an example profile, not as a private device record.
- Do not run local audits or cleanup commands from this repository unless the user explicitly asks for local execution.

## Editing

- Keep `skills/win11-storage-governance/SKILL.md` concise.
- Put detailed workflow material in one-level files under `skills/win11-storage-governance/references`.
- Keep the long human document in `docs/windows-11-c-drive-governance.md`.
- Use PowerShell-compatible examples for Windows operations.
- Avoid destructive scripts. Installers must not overwrite without an explicit force flag.

## Validation

- Run `python scripts/validate-pack.py .` after structural changes.
- When available, run the system `quick_validate.py` against `skills/win11-storage-governance`.
