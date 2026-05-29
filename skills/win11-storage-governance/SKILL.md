---
name: win11-storage-governance
description: Create safe, privacy-preserving Windows 11 C-drive cleanup, storage migration, cache relocation, package-manager policy, and maintenance plans. Use when the user asks about Win11 C盘清理, disk bloat, AppData, Windows Installer, WinSxS, WindowsApps/UWP, winget, Scoop, dev caches, browser profiles, NVIDIA shader cache, package caches, or recurring cleanup automation across one or many Windows 11 devices.
---

# Win11 Storage Governance

## Workflow

1. Clarify scope: template-only, audit-only, or execute-on-this-device. Default to template-only unless the user explicitly asks to inspect or change the local machine.
2. Load `references/safety-model.md` before recommending deletion, junctions, package-manager changes, or environment-variable changes.
3. Load `references/runbook.md` when producing a full plan, checklist, migration guide, or remediation sequence.
4. Load `references/device-profile-template.md` when the user wants a reusable template for another Windows 11 device.
5. Produce a staged plan: observe, classify, clean, migrate, automate, verify, rollback.

## Privacy Rules

- Do not read `%USERPROFILE%`, `AppData`, registry hives, package-manager state, shell history, environment variables, or local project folders unless the user explicitly requests a local audit/execution.
- Do not copy personal paths, usernames, machine names, package lists, logs, or environment values into reusable templates.
- When examples need paths, use neutral placeholders such as `<User>`, `<DownloadDrive>`, `<DevCacheRoot>`, and `<ModelDrive>`.
- Treat this repository's example device layout as a model pattern, not as a user's private configuration.

## Safety Gates

- Never recommend manually deleting or junctioning `C:\Windows\Installer`, `C:\Windows\WinSxS`, `C:\Program Files\WindowsApps`, the whole `AppData`, the whole user profile, or the whole `ProgramData`.
- Prefer official tools for Windows Update, WinSxS, Store/UWP apps, Visual Studio, drivers, and MSI repair.
- Use junctions only for clearly regenerable caches, with backup, testing, and rollback steps.
- For chat apps, browsers, password stores, databases, and device-bound app state, separate cache from user data before suggesting cleanup.
- For destructive commands, present a dry-run or staged quarantine approach unless the user explicitly asks to execute and the target is already classified.

## Output Contract

For a cleanup or migration plan, include:

- Risk classification: safe clean, official-tool clean, migrate/configure, investigate, do-not-touch.
- Concrete paths using placeholders unless doing an explicit local audit.
- Commands only where they are safe and scoped; otherwise give GUI/offical-tool instructions.
- Verification steps and rollback steps.
- A recurrence plan that uses allowlists and age thresholds instead of broad deletion.

For local execution, include:

- What will be inspected before running commands.
- What will be changed, quarantined, or left untouched.
- A summary of actions taken and remaining risks.

## References

- `references/safety-model.md`: deletion/migration red lines and risk categories.
- `references/runbook.md`: practical staged procedure for Windows 11 storage governance.
- `references/device-profile-template.md`: reusable profile template for adapting the plan to any Windows 11 device.
