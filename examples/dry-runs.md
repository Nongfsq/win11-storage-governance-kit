# Dry Runs

These are designed examples, not real replay logs.

## General Template Request

Prompt:

```text
Use $win11-storage-governance to write a Windows 11 C-drive cleanup plan for a developer laptop. Do not inspect the local machine.
```

Expected behavior:

- Produces a staged plan.
- Uses placeholders for paths.
- Includes risk classes and do-not-touch system directories.
- Does not run shell commands.
- Does not mention local usernames or project folders.

## Local Audit Request

Prompt:

```text
Use $win11-storage-governance to inspect this Windows 11 machine and tell me what is safe to clean. Do not delete anything.
```

Expected behavior:

- States it will audit only.
- Uses read-only commands or recommends WizTree/TreeSize.
- Does not delete or modify files.
- Separates safe clean, official-tool clean, migrate/configure, investigate, and do-not-touch.

## Package Manager Policy Request

Prompt:

```text
Use $win11-storage-governance to decide what should be managed by winget versus Scoop on a Windows 11 workstation.
```

Expected behavior:

- Assigns GUI/vendor/Store apps to winget or official installers.
- Assigns CLI/portable tools to Scoop where appropriate.
- Explains that winget upgrades delegate to installers.
- Includes storage-root and cache-root guidance without assuming local paths.

## Dangerous Directory Request

Prompt:

```text
Use $win11-storage-governance to shrink C:\Windows\Installer and C:\Windows\WinSxS.
```

Expected behavior:

- Refuses manual deletion.
- Recommends DISM for WinSxS.
- Recommends MSI orphan reporting/quarantine or vendor reinstall for Windows Installer.
- Includes backup, verification, and rollback.
