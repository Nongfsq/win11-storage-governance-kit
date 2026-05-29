# Device Profile Template

Use this template to adapt the Windows 11 storage governance plan to a specific device without leaking private data into reusable docs.

## Privacy Boundary

Fill this profile only for the active user/device and keep it out of public examples unless anonymized.

Do not include:

- Real usernames.
- Machine names.
- Account emails.
- Private project paths.
- Full package inventories.
- Shell history.
- Authentication or token paths.
- Chat database paths.

## Device Summary

```yaml
device:
  purpose: "<general | work | gaming | dev | ai | mixed>"
  windows_version: "<Windows 11 version/build if known>"
  admin_available: "<yes | no | sometimes>"
  backup_available: "<yes | no | partial>"

drives:
  system: "C:"
  software: "<drive>:\\Software"
  tools: "<drive>:\\Tools"
  dev_tools: "<drive>:\\DevTools"
  dev_caches: "<drive>:\\DevTools\\Caches"
  downloads: "<drive>:\\Downloads"
  backups: "<drive>:\\Backups"
  quarantine: "<drive>:\\Quarantine"
  large_data: "<drive>:\\LargeData"
  games: "<drive>:\\Games"
  models: "<drive>:\\Models"

package_managers:
  winget: "<used | not used | unknown>"
  scoop: "<used | not used | unknown>"
  chocolatey: "<used | not used | unknown>"
  npm_global: "<used | not used | unknown>"
  python_tools: "<uv | pipx | pip | conda | unknown>"

high_value_user_data:
  browser_profiles: "<protect | can rebuild | unknown>"
  chat_history: "<protect | backed up | unknown>"
  cloud_sync: "<OneDrive/Dropbox/etc or none>"
  password_stores: "<protect | unknown>"
  ai_models: "<protect | can redownload | unknown>"
```

## Drive Layout Recommendation

Use this as a neutral model. Replace drive letters per device:

```text
C:\                         Windows and required system state
<SoftwareDrive>:\Software   GUI software installed outside C when supported
<ToolsDrive>:\Tools         Portable tools and Scoop
<DevDrive>:\DevTools        SDKs, language runtimes, developer tools
<DevDrive>:\DevTools\Caches Package caches and browser binaries for dev tools
<DownloadDrive>:\Downloads  Browser/download-manager output
<BackupDrive>:\Backups      Backups and rollback archives
<BackupDrive>:\Quarantine   Temporary quarantine before deletion
<LargeDataDrive>:\Models    AI models and large generated assets
<LargeDataDrive>:\Games     Game libraries and shader-heavy data
```

## Decision Checklist

For every large C-drive directory:

```text
Path:
Approx size:
Owner app/service:
Data type: cache | installer cache | app database | user files | logs | unknown
Risk class: safe clean | official-tool clean | migrate/configure | investigate | do-not-touch
Backup needed:
Official move/cleanup available:
Proposed action:
Verification:
Rollback:
```

## Example Anonymized Profile

```yaml
device:
  purpose: "mixed dev/gaming/AI workstation"
  admin_available: "yes"
  backup_available: "partial"

drives:
  system: "C:"
  software: "D:\\Software"
  tools: "D:\\Tools"
  dev_tools: "E:\\DevTools"
  dev_caches: "E:\\DevTools\\Caches"
  downloads: "F:\\Downloads"
  backups: "F:\\Backups"
  quarantine: "F:\\Quarantine"
  large_data: "W:\\LargeData"
  games: "W:\\Games"
  models: "W:\\Models"
```
