# Windows 11 Storage Governance Runbook

Use this runbook to produce a plan for a Windows 11 device. Keep user-specific facts out of reusable output unless the user explicitly asks for a local audit.

## Phase 1: Define Scope

Ask or infer:

- Is this a template for any device, or an audit of the current device?
- Is the goal emergency space recovery, long-term governance, or both?
- Is the user comfortable with admin commands?
- Are there separate drives for software, tools, dev caches, downloads, models, or games?
- Are chat history, browser profiles, and password stores in scope?

If the user asks for a general template, do not inspect the local machine.

## Phase 2: Observe

For a local audit, prefer:

- WizTree, TreeSize, or Windows Storage Settings for first-pass sizing.
- PowerShell only for scoped checks.
- Package-manager commands that list state without changing it.

Common scoped commands:

```powershell
Get-PSDrive -PSProvider FileSystem
powercfg /a
Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore
winget upgrade
scoop status
```

Avoid broad recursive scans of private profile folders unless the user asked for local analysis.

## Phase 3: Classify

Classify every large item:

- Safe clean: temp/cache/regenerable.
- Official-tool clean: Windows/Store/VS/driver/MSI managed.
- Migrate/configure: downloads, package caches, game libraries, model caches.
- Investigate: app databases, chat data, browser profiles, indexers.
- Do-not-touch: system servicing and installer caches.

## Phase 4: Clean

Start with low-risk items:

1. Windows Settings temporary files.
2. Temp files older than a threshold.
3. Recycle Bin if approved.
4. Electron updater leftovers.
5. Package-manager caches.
6. Browser caches, not profile roots.
7. Driver download caches, not driver stores.
8. Hibernation only if not needed.

Use official tooling for WinSxS and Windows Update. Do not manually delete system servicing directories.

## Phase 5: Migrate

Use configuration before filesystem redirection:

- Downloads: browser and app settings.
- GUI software: uninstall/reinstall to a software drive.
- Small portable tools: Scoop or portable directory.
- Dev tools/caches: environment variables and package-manager config.
- Store apps: Windows Settings move.
- Games: launcher library manager.
- AI models: model manager or app settings.

Recommended neutral layout:

```text
<SystemDrive>:\        Windows and required system state
<SoftwareDrive>:\Software
<ToolsDrive>:\Tools
<DevDrive>:\DevTools
<DevDrive>:\DevTools\Caches
<DownloadDrive>:\Downloads
<BackupDrive>:\Backups
<LargeDataDrive>:\Models
<LargeDataDrive>:\Games
```

## Phase 6: Automate

Automate only allowlisted cleanup:

- Temp files older than N days.
- Known updater leftovers.
- Known cache directories.
- Package-manager cache cleanup commands.

Automation must:

- Log actions.
- Support dry-run where feasible.
- Avoid following junctions into unrelated trees.
- Avoid user databases and profile roots.

## Phase 7: Verify and Roll Back

After each migration:

- Launch the affected application.
- Run package-manager health checks.
- Confirm cache is being recreated at the new path.
- Keep backups/quarantines for a defined observation period.
- Document rollback steps.

## Output Shape

For a user-facing answer, prefer:

1. Short diagnosis.
2. Prioritized action table.
3. Commands or GUI paths.
4. Risk notes.
5. Verification and rollback.
6. Next maintenance cadence.
