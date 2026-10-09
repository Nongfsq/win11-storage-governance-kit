# Windows 11 Storage Governance Kit

[中文文档](README.zh-CN.md) | English

A Codex Skills kit for fixing Windows 11 system-drive bloat.

This project turns a practical Windows 11 C-drive cleanup workflow into a reusable agent skill and reference runbook. The core idea is not simply to delete files. It is to govern the system drive: classify what is safe to clean, move large regenerable caches away from `C:`, configure package managers and developer tools to use stable non-system locations, and keep Windows-managed directories under official maintenance paths.

## What Problem It Solves

Windows 11 machines often accumulate tens or hundreds of gigabytes under:

- `%TEMP%`, `C:\Windows\Temp`, update caches, and delivery optimization data.
- `AppData\Local` and `AppData\Roaming`.
- Electron updater leftovers and browser profile caches.
- `C:\Windows\Installer`, WinSxS, WindowsApps, and other system-managed stores.
- winget, Scoop, npm, pip, NuGet, Rust, Playwright, Puppeteer, Hugging Face, and Torch caches.
- NVIDIA/DirectX shader caches, game launchers, AI models, and developer SDKs.

Most cleanup guides treat these as isolated junk folders. That is not enough. The same bloat returns unless the machine has a storage policy.

This kit provides that policy.

## Core Principles

- **Observe before deleting.** Find the real large directories first.
- **Classify by risk.** Cache, app data, installer cache, system servicing data, and user files require different treatment.
- **Use official tools first.** WinSxS, Windows Update, Store/UWP apps, Visual Studio, drivers, and MSI repair should not be handled by blind filesystem deletion.
- **Migrate what will grow again.** Developer caches, package caches, downloads, models, game libraries, and shader caches should have explicit non-system locations.
- **Do not move whole system state.** Do not junction `C:\Windows\Installer`, `C:\Windows\WinSxS`, `C:\Program Files\WindowsApps`, the whole user profile, the whole `AppData`, or the whole `ProgramData`.
- **Protect privacy.** The skill defaults to template-only planning and does not inspect local user folders, registry, environment variables, logs, or package inventories unless explicitly asked.

## Repository Layout

```text
.
├── docs/
│   ├── windows-11-c-drive-governance.md
│   ├── compatibility.md
│   ├── trigger-tuning.md
│   └── ...
├── examples/
│   ├── dry-runs.md
│   ├── usage-benchmark.md
│   └── replay-log-template.md
├── scripts/
│   ├── install.ps1
│   └── validate-pack.py
├── skills/
│   └── win11-storage-governance/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
├── README.md
├── README.zh-CN.md
├── skill-pack.json
└── VERSION
```

## The Skill

Skill name:

```text
win11-storage-governance
```

Use it when the user asks about:

- Windows 11 C-drive bloat.
- `AppData`, `C:\Windows\Installer`, WinSxS, or WindowsApps.
- winget versus Scoop.
- Moving package-manager, developer, AI, browser, or shader caches.
- Designing a recurring cleanup policy.
- Creating a safe cleanup plan for one Windows 11 device or a fleet of similar devices.

The skill is intentionally concise. Detailed logic lives in:

- `skills/win11-storage-governance/references/safety-model.md`
- `skills/win11-storage-governance/references/runbook.md`
- `skills/win11-storage-governance/references/device-profile-template.md`

## Install the Codex Skill

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

Install to a custom skills root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -DestinationRoot "C:\Users\<User>\.codex\skills"
```

Overwrite an existing installed copy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Force
```

## Example Prompt

```text
Use $win11-storage-governance to create a safe Windows 11 C-drive cleanup and storage migration plan for a developer workstation. Do not inspect the local machine.
```

For a local audit, be explicit:

```text
Use $win11-storage-governance to inspect this Windows 11 machine and report what is safe to clean. Do not delete anything.
```

## Validation

Validate the pack:

```powershell
python .\scripts\validate-pack.py .
```

Validate the skill with Codex's system skill validator when available:

```powershell
python C:\Users\<User>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skills\win11-storage-governance
```

If your Python environment does not have `PyYAML`, run the validator through your preferred isolated tool runner, for example:

```powershell
uvx --with pyyaml python C:\Users\<User>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skills\win11-storage-governance
```

## Safety Notice

This project is conservative by design. It will not recommend manual deletion of Windows servicing stores or installer caches. In particular:

- Do not manually delete `C:\Windows\Installer`.
- Do not manually delete `C:\Windows\WinSxS`.
- Do not manually move `C:\Program Files\WindowsApps`.
- Do not junction the whole `AppData`, user profile, or `ProgramData`.

For high-risk areas, use official tools, vendor uninstallers, repair utilities, quarantine workflows, and rollback plans.

## Support

If this project is useful to you, you can buy me a coffee.

<a href="https://buymeacoffee.com/frankmenger"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="44"></a>

## License

MIT License.
