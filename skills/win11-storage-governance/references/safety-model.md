# Safety Model

Use this model before recommending deletion, migration, environment changes, package-manager changes, or recurring cleanup on Windows 11.

## Default Stance

- Prefer inspection and classification before cleanup.
- Prefer official app/system tools before filesystem surgery.
- Prefer migration by configuration before junctions.
- Prefer quarantine before deletion when the content is not plainly regenerable.
- Prefer placeholders in reusable materials. Do not include personal paths or local package inventories unless the user asks for a local audit.

## Risk Classes

### Safe Clean

Usually safe after closing related apps:

- `%TEMP%` files older than a chosen threshold.
- `C:\Windows\Temp` files older than a chosen threshold.
- Recycle Bin, when the user agrees.
- Electron updater leftovers such as `*-updater\pending` and stale installers.
- Browser `Cache`, `Code Cache`, and `GPUCache`.
- Package-manager caches after package-manager state is healthy.
- NVIDIA/DirectX shader caches, with the warning that games may recompile shaders.

### Official-Tool Clean

Use built-in or vendor tools:

- WinSxS: DISM `AnalyzeComponentStore` and `StartComponentCleanup`.
- Windows Update and Delivery Optimization: Windows Settings or Disk Cleanup.
- Hibernation file: `powercfg /a` then `powercfg /h off` only if hibernation/Fast Startup is not needed.
- Store/UWP apps: Windows Settings move/uninstall.
- Visual Studio packages/workloads: Visual Studio Installer.
- Adobe/Office/MSI repair chains: vendor cleaner, repair, uninstall, or reinstall.

### Migrate or Configure

Move by supported configuration first:

- Downloads directory.
- Browser download directory.
- Scoop root/cache.
- winget portable root and default download directory.
- npm/pnpm/pip/uv/NuGet/Rust/Bun/HuggingFace/Torch/Playwright/Puppeteer caches.
- Game libraries through Steam/Epic/Xbox settings.
- AI model directories through app settings or environment variables.

### Investigate First

Do not delete until classified:

- `AppData\Roaming` app data.
- Browser `IndexedDB`, extension data, and profile roots.
- Chat app directories and downloads.
- `ProgramData` service databases.
- Indexer databases.
- Installer caches that appear orphaned.

### Do Not Touch Manually

Do not manually delete or junction:

- `C:\Windows\Installer`
- `C:\Windows\WinSxS`
- `C:\Program Files\WindowsApps`
- Whole `%USERPROFILE%`
- Whole `AppData`
- Whole `ProgramData`
- Security software directories
- Driver stores and active driver service directories
- Password stores, authentication state, and device-bound app databases

## Junction Rule

Use junctions only when all are true:

1. The source is a cache or generated artifact.
2. The app is closed.
3. The target drive is stable and always mounted.
4. A backup or rename of the original directory is kept.
5. A rollback command is documented.
6. The app is tested immediately after the move.

Avoid junctions for chat apps, browser profile roots, app identities, databases, and system directories.
