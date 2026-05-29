# Windows 11 Storage Governance Kit：C 盘治理与迁移方案

> 目标：把 C 盘从“无限膨胀的系统垃圾场”治理成一个可预期、可维护、可恢复的系统盘。  
> 适用对象：普通 Win11 设备、重度软件用户、开发者工作站、AI/游戏/多浏览器 Profile 用户。  
> 核心原则：先识别、再分类、再清理；优先使用官方入口；只迁移可迁移的数据；对系统缓存和安装器缓存保持克制。

## 隐私与模板化声明

这份文档是通用模板，不应固化任何人的真实用户名、主目录、机器名、环境变量值、会话记录、软件登录状态或私有项目路径。文档中的盘符规划是一种匿名化的参考设备画像，用于展示如何把系统盘、普通软件、工具、开发缓存、下载和大文件分层管理。实际用于他人设备时，应先替换成对方自己的盘符、目录命名和备份策略。

除非用户明确要求“检查本机”或“在这台机器上执行”，否则基于本方案的 agent/脚本都应该只输出计划、模板和检查清单，不主动读取 `%USERPROFILE%`、`AppData`、注册表、环境变量或包管理器配置。

---

## 1. 总体原则

Windows 11 的 C 盘变大，通常不是单一原因，而是下面几类内容叠加：

1. 系统维护文件：`WinSxS`、Windows Update、Delivery Optimization、驱动残留、休眠文件。
2. 安装器缓存：`C:\Windows\Installer`、`C:\ProgramData\Package Cache`、Visual Studio/Adobe/MSI 补丁链。
3. 用户级应用数据：`AppData\Local`、`AppData\Roaming`、Electron updater、聊天软件、浏览器 Profile、UWP/Store 应用数据。
4. 包管理器和开发缓存：npm、pnpm、pip、uv、NuGet、Cargo/Rustup、Bun、Playwright、Puppeteer、HuggingFace、Torch。
5. 大型软件和游戏：Steam/Epic/Xbox/Store 游戏库、NVIDIA shader cache、游戏预编译缓存。
6. 下载器和同步软件：IDM、NeatDM、PikPak、OneDrive、QQ/微信文件、Zoom/Notion/Keet 等本地数据库。

治理 C 盘时要避免两种极端：

- 只靠“磁盘清理”按钮，结果清掉 2GB 后问题很快复发。
- 直接删系统目录或把整个 `AppData`、`WindowsApps`、`Windows\Installer` junction 到别的盘，短期省空间，长期破坏更新、卸载、修复和应用数据库。

正确做法是建立一套分层规则：

| 类别 | 操作倾向 | 例子 |
| --- | --- | --- |
| 临时文件、可再生缓存 | 可以清理或迁移 | `%TEMP%`、浏览器 Cache、Electron updater、package cache |
| 官方支持移动的应用/库 | 用官方入口迁移 | Store 应用、Steam 库、Xbox 库、Scoop root |
| 开发工具缓存 | 设环境变量迁移 | npm/pip/HF/Torch/Playwright/NuGet/Rust |
| 系统服务目录 | 只用官方维护工具 | WinSxS、Windows Update、Delivery Optimization |
| 安装器缓存 | 谨慎，优先卸载/修复/报告 | `C:\Windows\Installer`、Adobe MSP、VS Package Cache |
| 应用数据库/聊天记录 | 先备份，按应用规则处理 | WeChat、QQ、Keet、Notion、Zoom、Chrome Profile |

---

## 2. 先做体检：找出 C 盘真实大头

不要先猜，不要先删。第一步是定位空间被谁占用。

### 2.1 推荐工具

图形化工具适合第一轮排查：

- WizTree：很快，适合 NTFS 磁盘。
- TreeSize Free：适合逐层看目录。
- WinDirStat：直观但扫描慢。

建议以管理员身份运行，否则 `WindowsApps`、`System Volume Information`、部分 `ProgramData` 目录会显示不准。

### 2.2 PowerShell 快速检查

查看磁盘剩余空间：

```powershell
Get-PSDrive -PSProvider FileSystem |
  Select-Object Name,
    @{Name='UsedGB';Expression={[math]::Round($_.Used/1GB,2)}},
    @{Name='FreeGB';Expression={[math]::Round($_.Free/1GB,2)}},
    @{Name='TotalGB';Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}}
```

查看 C 盘根目录大项：

```powershell
$roots = @(
  'C:\Windows',
  'C:\Program Files',
  'C:\Program Files (x86)',
  'C:\ProgramData',
  "$env:USERPROFILE",
  'C:\Users\Public'
)

$roots | ForEach-Object {
  if (Test-Path -LiteralPath $_) {
    $size = (Get-ChildItem -LiteralPath $_ -Force -Recurse -ErrorAction SilentlyContinue |
      Measure-Object -Property Length -Sum).Sum
    [pscustomobject]@{
      Path = $_
      GB = [math]::Round($size / 1GB, 2)
    }
  }
} | Sort-Object GB -Descending
```

查看用户目录下一层大项：

```powershell
Get-ChildItem -LiteralPath $env:USERPROFILE -Force -Directory |
  ForEach-Object {
    $size = (Get-ChildItem -LiteralPath $_.FullName -Force -Recurse -ErrorAction SilentlyContinue |
      Measure-Object -Property Length -Sum).Sum
    [pscustomobject]@{
      Path = $_.FullName
      GB = [math]::Round($size / 1GB, 2)
    }
  } | Sort-Object GB -Descending | Select-Object -First 30
```

注意：PowerShell 递归统计在很大的目录上会慢。真实工作中，优先用 WizTree/TreeSize 找大头，再用 PowerShell 针对具体目录复核。

---

## 3. 安全级别：哪些能删，哪些不能碰

### 3.1 通常可以清理

这些目录一般是临时文件或可再生成缓存，但仍建议只删“旧文件”，不要在程序运行时强删：

- `%TEMP%`
- `C:\Windows\Temp`
- 回收站
- Electron updater 残留：`%LOCALAPPDATA%\*-updater`
- 浏览器 Cache：Chrome/Edge/Firefox 的 `Cache`、`Code Cache`、`GPUCache`
- npm/pnpm/pip/uv/NuGet/Rust/Playwright/Puppeteer 等工具缓存
- NVIDIA `DXCache`、`GLCache`、shader cache，前提是接受下次启动游戏重新编译
- 下载器临时文件、残留安装包
- Windows Delivery Optimization cache，优先通过系统设置清

推荐删除 7 天以前的临时文件，而不是无差别清空：

```powershell
$cutoff = (Get-Date).AddDays(-7)
$targets = @($env:TEMP, 'C:\Windows\Temp')

foreach ($target in $targets) {
  if (Test-Path -LiteralPath $target) {
    Get-ChildItem -LiteralPath $target -Force -ErrorAction SilentlyContinue |
      Where-Object { $_.LastWriteTime -lt $cutoff } |
      Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
  }
}
```

### 3.2 应该通过官方入口清理

这些区域不要手动删文件，应使用 Windows 或软件自己的维护工具：

- Windows Update / Delivery Optimization：
  - 设置 > 系统 > 存储 > 临时文件
  - 设置 > 系统 > 存储 > 存储感知
- WinSxS：
  - `Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore`
  - `Dism.exe /Online /Cleanup-Image /StartComponentCleanup`
- 休眠文件：
  - `powercfg /a`
  - `powercfg /h off`
- Visual Studio：
  - Visual Studio Installer 修改/卸载 workload
  - VS 自带清理工具或重装
- Microsoft Store / UWP 应用：
  - 设置 > 应用 > 已安装的应用 > 移动
  - 设置 > 系统 > 存储 > 高级存储设置 > 新内容保存位置

### 3.3 不要手动删除或整体迁移

这些是高风险目录：

- `C:\Windows\Installer`
- `C:\Windows\WinSxS`
- `C:\Program Files\WindowsApps`
- `C:\ProgramData\Package Cache`
- 整个 `C:\Users\<User>\AppData`
- 整个 `C:\ProgramData`
- 整个用户目录 `C:\Users\<User>`
- 安全软件、驱动程序、系统服务目录
- 聊天记录/数据库目录，除非已确认内容和备份方式

尤其是 `C:\Windows\Installer`：这是 MSI/MSP 的安装器缓存。很多软件的卸载、修复、升级都依赖它。手动删除可能导致以后无法卸载、无法升级、无法修复，甚至 Windows Installer 反复要求原始安装包。这个目录只能做“孤儿文件报告和谨慎隔离”，不能直接一把删，也不建议 junction 到别的盘。

---

## 4. 第一轮清理：低风险、立刻见效

这一轮目标是 30 分钟内释放一部分空间，不改变系统结构。

### 4.1 打开存储感知

路径：

```text
设置 > 系统 > 存储 > 存储感知
```

建议：

- 开启存储感知。
- 临时文件清理打开。
- 下载文件夹不要自动清，除非你有明确的下载归档习惯。
- 回收站可以设置 30 天或 60 天。

### 4.2 清 Windows 临时文件和更新缓存

路径：

```text
设置 > 系统 > 存储 > 临时文件
```

可选项目通常包括：

- Windows Update 清理
- Delivery Optimization 文件
- 临时文件
- 缩略图
- DirectX Shader Cache
- 回收站

不确定时不要勾选“下载”。

### 4.3 清用户和系统 Temp

用上面“只删 7 天前”的 PowerShell 脚本即可。正在运行的软件可能锁定部分文件，失败可以忽略。

### 4.4 清 Electron updater 残留

很多 Electron 应用会在 `%LOCALAPPDATA%` 下留下 updater 目录，例如：

- `jan-updater`
- `pencil-updater`
- `memo-updater`
- `termius-updater`
- `xyz.chatboxapp.app-updater`

典型可清理内容：

- `pending`
- `installer.exe`
- 旧版本安装包
- updater 临时目录

原则：

- 关闭对应软件后清。
- 只清 updater 目录，不清应用主数据目录。
- 清完后打开软件确认更新功能正常。

### 4.5 关闭休眠释放 hiberfil.sys

如果你不用休眠，也不依赖快速启动，可以关闭：

```powershell
powercfg /a
powercfg /h off
```

效果：

- 删除或释放 `C:\hiberfil.sys`。
- 通常能释放几 GB 到几十 GB，取决于内存大小。
- 会同时关闭 Windows 快速启动。

如果你需要恢复：

```powershell
powercfg /h on
```

---

## 5. 第二轮清理：Windows 系统组件

### 5.1 WinSxS

`C:\Windows\WinSxS` 是组件存储，不是普通缓存。不要手动删。

先分析：

```powershell
Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore
```

再清理：

```powershell
Dism.exe /Online /Cleanup-Image /StartComponentCleanup
```

高级选项：

```powershell
Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase
```

`/ResetBase` 会让已安装更新的旧版本无法卸载，适合系统稳定、近期不打算回滚更新的机器。普通用户不建议默认使用。

### 5.2 Windows Update 和 Delivery Optimization

优先用设置里的“临时文件”清。不要手动删除 `SoftwareDistribution`，除非 Windows Update 本身损坏，需要按修复流程停止服务、重命名目录、重启服务。

### 5.3 系统还原点和影子副本

如果 `System Volume Information` 很大，通常是还原点、影子副本、备份软件造成的。

查看影子副本：

```powershell
vssadmin list shadowstorage
```

可以通过图形界面限制系统保护占用：

```text
控制面板 > 系统 > 系统保护 > 配置
```

不要在不了解备份策略时直接清空所有还原点。

---

## 6. `C:\Windows\Installer`：最容易误删的大坑

### 6.1 它是什么

`C:\Windows\Installer` 保存 Windows Installer 使用的 `.msi` 和 `.msp` 缓存。它不是普通下载缓存。它被用于：

- 卸载软件
- 修复软件
- 修改组件
- 安装补丁
- 升级软件
- 回滚某些安装状态

所以这个目录大，不等于能删。

### 6.2 正确处理方式

优先级从高到低：

1. 卸载不需要的软件。
2. 对特别大的软件做“干净卸载后重装”，例如 Adobe Acrobat、旧版 Office、旧版 SDK。
3. 使用官方修复/卸载工具，例如 Microsoft Program Install and Uninstall troubleshooter、Adobe Cleaner、Visual Studio Installer。
4. 生成 orphaned MSI/MSP 报告，只隔离注册表不再引用的文件。
5. 隔离后观察一段时间，再删除隔离目录。

不要做：

- 不要手动全删。
- 不要用磁盘清理软件无脑清。
- 不要把整个 `C:\Windows\Installer` junction 到其他盘。
- 不要用压缩包替换原目录。

### 6.3 孤儿文件可以怎么处理

孤儿 MSI/MSP 指的是：文件仍在 `C:\Windows\Installer`，但注册表里找不到对应引用。它们可能来自卸载残留或损坏安装记录。

安全做法不是删除，而是：

1. 扫描生成报告。
2. 只移动到隔离目录，例如 `F:\File\Quarantine\WindowsInstaller\YYYYMMDD-HHMMSS`。
3. 保留恢复脚本。
4. 使用电脑几天到几周，确认安装/卸载/更新不报错。
5. 再决定删除隔离目录。

如果剩下的大头是仍被注册表引用的补丁链，例如 Adobe Acrobat 的 `.msp` 链，通常不应直接删。最干净的方案是卸载该软件，用官方清理工具清残留，再安装最新版。

---

## 7. `Program Files`、`ProgramData` 和普通软件

### 7.1 `C:\Program Files`

这里通常是真正安装的软件。处理思路：

- 不要手动搬目录。
- 优先卸载不用的软件。
- 重新安装到目标盘，例如 `D:\Software`。
- 对支持 portable 的工具，改用 Scoop 或手动 portable 目录。
- 对开发工具，优先安装到 `E:\DevTools`。

适合迁出的软件：

- 大型 GUI 软件：安装到 `D:\Software`
- 小型工具：安装到 `D:\Tools`
- 开发工具链：安装到 `E:\DevTools`
- 游戏和大型素材：安装到专用盘或 `W:`

不适合手动迁出的软件：

- 驱动
- 安全软件
- Office/Adobe 等复杂 MSI 软件
- 依赖系统服务的软件
- Store/UWP 的 `WindowsApps`

### 7.2 `C:\ProgramData`

`ProgramData` 是全用户数据目录，经常包含：

- 安装器缓存
- 更新器缓存
- 索引库
- 驱动下载缓存
- 服务数据库
- 模型/资源文件

可清理例子：

- `C:\ProgramData\NVIDIA Corporation\Downloader`：通常是 NVIDIA 安装包下载缓存，可在不运行安装器时清理。
- 旧安装包、旧日志。

需要谨慎例子：

- `C:\ProgramData\Microsoft\VisualStudio\Packages`：Visual Studio 包缓存，优先用 VS Installer 清理或修改 workload。
- 索引器数据库，例如 Fluent Search：先看软件设置是否支持移动索引位置。若不支持，关闭服务/软件后再考虑 junction，并保留回滚。
- 安全软件、驱动服务数据库：不要手动删。

---

## 8. `AppData`：为什么不能整体搬

`AppData` 很大，但不建议把整个目录迁移到别的盘。

原因：

1. Windows、UWP、Electron、浏览器、聊天软件都假设它在用户 Profile 下。
2. 一些应用使用文件锁、设备 ID、数据库 WAL、加密存储、DPAPI、路径校验。
3. Junction 可能让应用误判文件被篡改。
4. 更新器、卸载器、Store 应用、服务进程可能不跟随迁移。
5. 一旦目标盘未挂载、权限变化、杀毒拦截，应用可能损坏数据。

更好的策略：

- 清 cache，不清 data。
- 用应用设置改路径。
- 对明确可再生成缓存使用 junction。
- 对用户级安装软件，通过重装迁移到 `D:\Software` 或 `E:\DevTools`。
- 对聊天记录/数据库先备份，再按应用规则迁移。

### 8.1 `AppData\Local`

常见内容：

- 应用缓存
- 浏览器 Cache
- Electron updater
- 用户级安装软件：`AppData\Local\Programs`
- 临时目录
- GPU/DirectX Cache

可以重点看：

- `%LOCALAPPDATA%\Temp`
- `%LOCALAPPDATA%\Programs`
- `%LOCALAPPDATA%\*-updater`
- `%LOCALAPPDATA%\Google\Chrome\User Data\*\Cache`
- `%LOCALAPPDATA%\Microsoft\Edge\User Data\*\Cache`
- `%LOCALAPPDATA%\pip\Cache`
- `%LOCALAPPDATA%\npm-cache`
- `%LOCALAPPDATA%\pnpm`
- `%LOCALAPPDATA%\ms-playwright`

### 8.2 `AppData\Roaming`

常见内容：

- 用户配置
- 聊天记录
- 应用数据库
- 同步状态
- Electron 应用数据

这里比 Local 更危险。不要看到大就删。尤其注意：

- WeChat / 微信
- Tencent / QQ
- Keet / Pear
- Notion
- Zoom
- Discord/Slack/Teams
- IDM/下载器历史

对于聊天软件，必须先区分：

- cache：可清
- logs：可清或压缩
- downloads：可迁移
- database：不要直接删
- identity/security/device marker：不要 junction 或修改

### 8.3 Keet/Pear 的教训

某些应用会校验本地数据库或设备文件。把它们的 Roaming 数据整体 junction 到其他盘后，可能出现类似：

```text
Invalid device file, was modified
```

这说明应用认为关键文件被移动、替换或篡改。对这类应用：

- 不要整体 junction。
- 不要手动改数据库目录。
- 优先让它留在 C 盘。
- 只能清日志、旧缓存、下载附件。
- 如果必须迁移，先查应用官方是否支持数据目录设置。

---

## 9. UWP / Store 应用和 `WindowsApps`

`C:\Program Files\WindowsApps` 是 Microsoft Store / UWP / MSIX 应用目录。不能手动改权限后删除或搬迁。

正确做法：

1. 设置 > 应用 > 已安装的应用。
2. 找到应用。
3. 如果有“移动”按钮，移动到其他盘。
4. 设置 > 系统 > 存储 > 高级存储设置 > 新内容保存位置。
5. 将“新应用将保存到”改为非 C 盘。

注意：

- 不是所有 Store 应用都支持移动。
- 已安装应用是否能移动取决于应用包、系统策略和安装方式。
- 游戏类 Store/Xbox 内容要优先使用 Xbox app 或 Microsoft Store 的移动/安装位置设置。
- 不要手动搬 `WindowsApps` 文件夹。

---

## 10. winget 与 Scoop：谁管理什么

### 10.1 winget 的定位

winget 是 Windows Package Manager，适合管理：

- GUI 软件
- 厂商安装器
- MSI/EXE 安装包
- MSIX/Store 来源应用
- 普通用户软件

常用命令：

```powershell
winget search 7zip
winget install 7zip.7zip
winget upgrade
winget upgrade --all
winget uninstall <package-id>
winget list
```

winget 升级的本质通常是：

- 下载新版官方安装器；
- 用静默参数运行；
- 让软件自己的 MSI/EXE/MSIX 安装逻辑完成升级。

所以它很像“软件自己打开后点击更新”，但区别是：

- winget 统一发现版本和触发安装。
- 实际安装仍依赖每个软件自己的 installer。
- 如果软件的 MSI 记录损坏、旧缓存缺失、权限不对，winget 也会失败，例如 exit code 1603。

winget 适合：

- 7-Zip
- Chrome/Edge/Firefox
- Git
- VS Code
- PowerShell
- OBS
- Zoom
- Adobe/腾讯/普通 GUI 软件，前提是 manifest 质量可靠

winget 不适合：

- 需要精细版本隔离的 CLI 工具
- 需要完全 portable 管理的开发工具
- 对安装路径要求强、安装器又不支持路径参数的软件

### 10.2 winget 的路径控制

winget 支持一些设置项，例如：

- 默认下载目录：`downloadBehavior.defaultDownloadDirectory`
- portable 包根目录：`installBehavior.portablePackageUserRoot`
- 系统级 portable 包根目录：`installBehavior.portablePackageMachineRoot`
- 需要显式安装路径的软件默认安装根目录：`installBehavior.defaultInstallRoot`

编辑设置：

```powershell
winget settings
```

也可以导出当前设置供备份/对照：

```powershell
winget settings export
```

示例思路：

```json
{
  "installBehavior": {
    "defaultInstallRoot": "D:\\Software",
    "portablePackageUserRoot": "D:\\Tools\\WingetPortable",
    "portablePackageMachineRoot": "D:\\Tools\\WingetPortableMachine"
  },
  "downloadBehavior": {
    "defaultDownloadDirectory": "F:\\File\\Download\\winget"
  }
}
```

注意：

- 这不等于所有软件都会安装到该目录。
- 普通 MSI/EXE 是否支持安装位置，取决于安装器本身。
- `--location` 对部分安装器有效，对部分无效。
- Store/MSIX 应用走 Windows 应用安装机制。

### 10.3 Scoop 的定位

Scoop 更像 Windows 上的 Homebrew，适合管理：

- CLI 工具
- portable 软件
- 开发工具
- 小型工具
- 无复杂系统服务的软件

Scoop 的优点：

- 安装目录清晰。
- 版本目录清晰。
- shim 管理命令入口。
- 卸载相对干净。
- cache 可以清理。
- 很适合放到非 C 盘。

常用命令：

```powershell
scoop update
scoop update *
scoop cleanup *
scoop cache rm *
scoop uninstall <app>
scoop list
```

建议路径：

```powershell
$env:SCOOP = 'D:\Tools\Scoop'
$env:SCOOP_GLOBAL = 'D:\Tools\ScoopGlobal'
```

如果是开发工具，也可以放在：

```text
E:\DevTools\Scoop
E:\DevTools\ScoopGlobal
```

### 10.4 实用分工

推荐分工：

| 软件类型 | 首选 |
| --- | --- |
| 普通 GUI 软件 | winget |
| Store/UWP/MSIX | Microsoft Store / winget |
| CLI 工具 | Scoop |
| portable 小工具 | Scoop |
| Node/Python/Rust 等生态工具 | 对应生态工具 + 缓存迁移 |
| 大型 IDE | 官方安装器，路径设到 D/E |
| 游戏 | Steam/Epic/Xbox 官方库管理 |
| 驱动 | 厂商工具或 Windows Update |

---

## 11. 开发缓存统一迁移

开发者机器的 C 盘膨胀，常见元凶是包缓存、浏览器二进制、模型缓存。建议统一迁到：

```text
E:\DevTools\Caches
```

### 11.1 npm

```powershell
npm config set prefix E:\DevTools\npm-global
npm config set cache E:\DevTools\Caches\npm
npm cache verify
```

确认：

```powershell
npm config get prefix
npm config get cache
```

### 11.2 pnpm

```powershell
pnpm config set store-dir E:\DevTools\Caches\pnpm-store
```

确认：

```powershell
pnpm config get store-dir
```

### 11.3 pip

临时清理：

```powershell
pip cache dir
pip cache purge
```

长期迁移可以设置用户环境变量：

```powershell
[Environment]::SetEnvironmentVariable('PIP_CACHE_DIR', 'E:\DevTools\Caches\pip', 'User')
```

### 11.4 uv

```powershell
[Environment]::SetEnvironmentVariable('UV_CACHE_DIR', 'E:\DevTools\Caches\uv', 'User')
```

### 11.5 HuggingFace

```powershell
[Environment]::SetEnvironmentVariable('HF_HOME', 'E:\DevTools\Caches\huggingface', 'User')
[Environment]::SetEnvironmentVariable('HF_HUB_CACHE', 'E:\DevTools\Caches\huggingface\hub', 'User')
```

### 11.6 Torch

```powershell
[Environment]::SetEnvironmentVariable('TORCH_HOME', 'E:\DevTools\Caches\torch', 'User')
```

### 11.7 Playwright

```powershell
[Environment]::SetEnvironmentVariable('PLAYWRIGHT_BROWSERS_PATH', 'E:\DevTools\Caches\ms-playwright', 'User')
```

迁移后需要重新安装浏览器：

```powershell
playwright install
```

### 11.8 Puppeteer

```powershell
[Environment]::SetEnvironmentVariable('PUPPETEER_CACHE_DIR', 'E:\DevTools\Caches\puppeteer', 'User')
```

### 11.9 NuGet / .NET

清理：

```powershell
dotnet nuget locals all --clear
```

迁移全局包目录：

```powershell
[Environment]::SetEnvironmentVariable('NUGET_PACKAGES', 'E:\DevTools\Caches\nuget\packages', 'User')
```

### 11.10 Rust / Cargo / rustup

适合新机器或重装前设置：

```powershell
[Environment]::SetEnvironmentVariable('CARGO_HOME', 'E:\DevTools\Caches\cargo', 'User')
[Environment]::SetEnvironmentVariable('RUSTUP_HOME', 'E:\DevTools\Caches\rustup', 'User')
```

如果已经安装 Rust，迁移前先关闭相关终端和 IDE，再移动目录，并测试：

```powershell
rustc --version
cargo --version
```

### 11.11 Bun

Bun 的安装目录通常由 `BUN_INSTALL` 控制。缓存变量需要按当前 Bun 版本确认。可采用：

```powershell
[Environment]::SetEnvironmentVariable('BUN_INSTALL', 'E:\DevTools\Bun', 'User')
```

如当前版本支持 `BUN_CACHE_DIR`，可以设置：

```powershell
[Environment]::SetEnvironmentVariable('BUN_CACHE_DIR', 'E:\DevTools\Caches\bun', 'User')
```

### 11.12 迁移后的注意事项

设置用户环境变量后：

1. 关闭所有终端、IDE、Codex、VS Code、JetBrains。
2. 重新打开终端。
3. 用工具自己的 `config get` 或 `cache dir` 命令确认路径。
4. 再清理 C 盘旧缓存。

不要在设置没生效前删除旧缓存。

---

## 12. 浏览器、Chrome Profile 和缓存

Chrome/Edge 的空间通常来自：

- 多 Profile
- Cache
- Code Cache
- GPUCache
- Service Worker cache
- IndexedDB
- Extension data
- Crash reports

清理策略：

- 多 Profile 是用户资产，不要整体删。
- Cache、Code Cache、GPUCache 可清。
- IndexedDB 可能包含离线应用数据，不要无脑删。
- Extension data 可能包含插件配置，不要无脑删。

Chrome 本体可以通过 winget 或官方安装器管理；但 Chrome User Data 默认仍在用户目录。把整个 Chrome Profile junction 到别的盘风险较高，尤其是你有很多 Profile、登录态、扩展和 Web 应用数据时。

低风险做法：

1. 保留 Profile 在 C。
2. 定期清各 Profile 的 `Cache`、`Code Cache`、`GPUCache`。
3. 对下载目录迁移到 `F:\File\Download`。
4. 对浏览器临时测试 Profile 放到项目或缓存盘。

---

## 13. NVIDIA、DirectX Shader Cache 和游戏预编译

NVIDIA/DirectX 缓存常见位置：

- `%LOCALAPPDATA%\NVIDIA\DXCache`
- `%LOCALAPPDATA%\NVIDIA\GLCache`
- `%LOCALAPPDATA%\D3DSCache`
- `C:\ProgramData\NVIDIA Corporation\Downloader`

### 13.1 可以清理什么

通常可清：

- NVIDIA Downloader 旧安装包。
- DXCache/GLCache/D3DSCache。
- DirectX Shader Cache。

代价：

- 下次打开游戏或 3D 软件可能重新编译 shader。
- 某些 3A 游戏首次加载会变慢。

### 13.2 Shader Cache Size 是什么

NVIDIA 控制面板里的 Shader Cache Size 控制驱动 shader cache 的上限。设成 100GB 表示允许缓存增长到更大，减少频繁重编译，但如果默认缓存仍在 C 盘，就可能继续吃 C 盘。

### 13.3 能不能迁移到 W 盘

可以对特定缓存目录使用 NTFS junction，但只建议迁移“可再生成缓存”，不要迁移驱动主目录。

示例思路：

```powershell
$source = "$env:LOCALAPPDATA\NVIDIA\DXCache"
$target = "W:\Caches\NVIDIA\DXCache"

New-Item -ItemType Directory -Force -Path $target | Out-Null
if (Test-Path -LiteralPath $source) {
  Rename-Item -LiteralPath $source -NewName "DXCache.backup"
}
cmd /c mklink /J "$source" "$target"
```

迁移后测试：

- 打开 NVIDIA 控制面板。
- 启动 1-2 个常用游戏。
- 观察是否报错、是否能生成缓存。
- 一周后删除 `.backup`。

回滚：

```powershell
Remove-Item "$env:LOCALAPPDATA\NVIDIA\DXCache" -Force
Rename-Item "$env:LOCALAPPDATA\NVIDIA\DXCache.backup" "DXCache"
```

如果遇到游戏异常、反作弊异常、驱动更新异常，应回滚。

---

## 14. 下载器、聊天软件、同步软件

这些软件经常在 C 盘留下大量数据，但“数据类型”差异很大。

### 14.1 IDM / NeatDM / 下载器

重点检查：

- 临时下载目录
- 未完成下载
- 历史缓存
- 旧安装包
- 浏览器捕获缓存

建议：

- 把默认下载目录改到 `F:\File\Download`。
- 不再使用的软件先卸载，再删除残留目录。
- 删除前看是否有未完成下载或需要保留的文件。

### 14.2 QQ / WeChat / Tencent

不要看到 `Tencent` 大就删。里面可能有：

- 聊天图片
- 文件
- 视频
- 表情
- 小程序缓存
- 日志
- 数据库

建议：

- 先在 QQ/微信设置里迁移文件管理目录。
- 清理缓存使用软件内置功能。
- 导出或确认聊天记录备份后再处理数据库。

### 14.3 Zoom / Notion / Teams / Slack

通常包含：

- Cache
- logs
- crash reports
- IndexedDB
- 离线数据
- 插件数据

可清：

- Cache
- GPUCache
- Code Cache
- logs
- crash dumps

谨慎：

- IndexedDB
- Local Storage
- databases

### 14.4 Keet / Pear

Keet/Pear 类应用可能使用本地数据库和设备文件校验。建议：

- 保留主数据在默认位置。
- 只清日志和可识别缓存。
- 不要整体 junction。
- 不要修改 `CORESTORE`、identity、device marker 等关键文件。

---

## 15. 大型开发 IDE 和用户级安装软件

### 15.1 `AppData\Local\Programs`

很多用户级安装软件默认安装到：

```text
C:\Users\<User>\AppData\Local\Programs
```

例如：

- Notion
- Termius
- Loom
- Cursor/Trae/Antigravity 类编辑器
- Memo
- OpenCode 桌面版
- 一些 Electron 应用

治理方式：

1. 用应用自带卸载器或 winget 卸载。
2. 删除残留 updater/cache。
3. 重新安装到 `D:\Software` 或 `E:\DevTools`。
4. 如果安装器不支持路径，考虑 Scoop/portable 版本。

不要直接把 `AppData\Local\Programs` 整体 junction 到 D 盘。里面的软件更新器、卸载器、快捷方式和注册表记录复杂，整体迁移容易制造坏安装记录。

### 15.2 JetBrains / VS / SDK

JetBrains：

- IDE 本体可安装到非 C 盘。
- caches、logs、plugins 可通过 JetBrains Toolbox 或 IDE 设置管理。
- 卸载旧 IDE 后清理旧缓存。

Visual Studio：

- 安装位置和 download cache 在安装器中设置。
- 旧 workload 通过 Visual Studio Installer 删除。
- `C:\ProgramData\Microsoft\VisualStudio\Packages` 不要直接无脑删，优先使用 VS Installer 管理。

SDK：

- 旧 Android SDK、Windows SDK、CUDA、Node/Python/Rust 工具链都可能很大。
- 每种工具用自己的卸载器或版本管理器清理。

---

## 16. AI 模型和大缓存

AI/ML 工具很容易把 C 盘塞满：

- HuggingFace models
- Torch hub
- Transformers cache
- Diffusers cache
- Ollama models
- LM Studio models
- ComfyUI models
- npm/pip wheel cache

建议统一：

```text
E:\DevTools\Caches
W:\Models
```

示例：

```powershell
[Environment]::SetEnvironmentVariable('HF_HOME', 'E:\DevTools\Caches\huggingface', 'User')
[Environment]::SetEnvironmentVariable('TORCH_HOME', 'E:\DevTools\Caches\torch', 'User')
```

对于模型本体，建议放：

```text
W:\Models
```

不要把模型放在 `AppData` 或项目目录里长期堆积。

---

## 17. Junction 的使用边界

NTFS junction 是强工具，但不能滥用。

### 17.1 适合 junction 的对象

- 可再生成缓存
- 大型下载缓存
- 游戏 shader cache
- 明确不含身份/数据库的工具 cache
- 软件官方不支持改路径，但缓存结构简单

### 17.2 不适合 junction 的对象

- 整个 `AppData`
- 整个用户目录
- `C:\Windows\Installer`
- `C:\Windows\WinSxS`
- `WindowsApps`
- 数据库目录
- 聊天记录目录
- 身份认证目录
- 安全软件目录
- 驱动目录

### 17.3 标准迁移流程

```powershell
$source = 'C:\Path\To\Cache'
$target = 'E:\DevTools\Caches\AppName\Cache'
$backup = "$source.backup"

# 1. 关闭相关软件
# 2. 创建目标目录
New-Item -ItemType Directory -Force -Path $target | Out-Null

# 3. 移动旧目录为备份
Rename-Item -LiteralPath $source -NewName (Split-Path $backup -Leaf)

# 4. 创建 junction
cmd /c mklink /J "$source" "$target"

# 5. 测试应用
# 6. 稳定后删除 backup
```

回滚：

```powershell
Remove-Item -LiteralPath 'C:\Path\To\Cache' -Force
Rename-Item -LiteralPath 'C:\Path\To\Cache.backup' -NewName 'Cache'
```

---

## 18. 自动化定期清理

自动化的目标是控制复发，而不是自动删除一切。

### 18.1 可以定期清理的内容

建议每周或每月清：

- `%TEMP%` 中超过 7 天的文件
- `C:\Windows\Temp` 中超过 7 天的文件
- Electron updater `pending`、旧 `installer.exe`
- Chrome/Edge Cache、Code Cache、GPUCache
- Notion/Zoom/Teams/Slack 的 Cache、logs
- npm/pnpm/pip/uv 缓存，按需要
- NVIDIA Downloader 旧安装包

### 18.2 不应自动清理的内容

不要计划任务自动删：

- `Roaming` 下不明应用数据
- 微信/QQ/Keet/Notion 数据库
- Chrome IndexedDB
- `Windows\Installer`
- `WinSxS`
- `WindowsApps`
- `ProgramData` 下不明服务目录
- 任何未备份的用户文件

### 18.3 脚本应有日志和白名单

好的清理脚本应具备：

- 明确 allowlist。
- 只删超过 N 天的文件。
- 支持 `-WhatIf` 预演。
- 输出日志。
- 遇到锁定文件跳过。
- 不追踪 junction 进入别的盘误删。
- 不删除目录本身，只删除匹配文件或已知缓存子目录。

---

## 19. 推荐盘符规划

可按机器情况调整。一个适合重度用户/开发者的规划：

```text
C:\        Windows、驱动、必要系统组件、少量必须留在 C 的应用数据
D:\Software 普通 GUI 软件
D:\Tools    小型工具、portable 工具、Scoop
E:\DevTools 开发工具链、SDK、开发缓存
F:\File     下载、备份、隔离区、文档归档
W:\         游戏、大模型、shader cache、大型素材
```

具体例子：

```text
F:\File\Download\winget
F:\File\Quarantine\WindowsInstaller
E:\DevTools\Caches\npm
E:\DevTools\Caches\pip
E:\DevTools\Caches\huggingface
E:\DevTools\Caches\ms-playwright
D:\Tools\Scoop
D:\Software\Notion
W:\Caches\NVIDIA
W:\Models
```

---

## 20. 一套可执行的治理流程

### 第一阶段：低风险释放空间

1. 用 WizTree/TreeSize 扫描 C 盘。
2. 记录前 20 个大目录。
3. 设置 > 系统 > 存储 > 临时文件，清 Windows 临时项。
4. 删除 7 天前的 `%TEMP%` 和 `C:\Windows\Temp`。
5. 清 Electron updater 残留。
6. 如果不用休眠，执行 `powercfg /h off`。
7. 清下载器旧临时文件。
8. 清 npm/pip/pnpm/uv/NuGet 等缓存。

### 第二阶段：迁移会复发的大头

1. 把下载目录改到 `F:\File\Download`。
2. 配置 winget 默认下载目录和 portable root。
3. 把 Scoop root 放到 `D:\Tools` 或 `E:\DevTools`。
4. 把开发缓存迁到 `E:\DevTools\Caches`。
5. 把 AI 模型迁到 `W:\Models`。
6. 把游戏库迁到专用盘。
7. Store 应用通过设置移动。
8. 大型 GUI 软件卸载后重装到 `D:\Software`。

### 第三阶段：处理系统和安装器大头

1. `Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore`
2. `Dism.exe /Online /Cleanup-Image /StartComponentCleanup`
3. 检查 `C:\Windows\Installer`，只做 orphan report，不直接删。
4. 对 Adobe/Office/VS 等大补丁链，考虑干净卸载重装。
5. Visual Studio 用 Installer 修改 workload 和缓存。
6. 对 `ProgramData` 大目录逐个识别。

### 第四阶段：建立防复发机制

1. 开启 Storage Sense。
2. 建立每周清理任务，只清 allowlist。
3. 每月跑一次 C 盘 top directories 报告。
4. 新软件优先问：能否安装到 D/E？能否用 Scoop？缓存能否改路径？
5. 每季度检查：
   - `AppData\Local`
   - `AppData\Roaming`
   - `ProgramData`
   - `Windows\Installer`
   - 浏览器 Profile
   - AI/dev caches

---

## 21. 典型问题判断

### 21.1 winget 升级报 1603

1603 是 Windows Installer 常见失败码，通常不是 winget 自己的问题，而是安装器失败。常见原因：

- 旧 MSI/MSP 缓存缺失。
- 注册表安装记录损坏。
- 软件正在运行。
- 权限不足。
- 安装器检测到旧版本残留。
- 安装路径或服务状态异常。

处理顺序：

1. 重启。
2. 管理员终端运行。
3. 关闭目标软件和相关服务。
4. 看 winget 日志。
5. 用应用官方卸载器或 Microsoft Program Install and Uninstall troubleshooter 清坏记录。
6. 卸载后重装最新版。

### 21.2 “我明明装在其他盘，为什么 C 盘还有它？”

可能原因：

- 主程序在 D，但用户数据在 C。
- Store/UWP 包在 `WindowsApps`。
- shader/cache 在 C。
- 安装器缓存仍在 C。
- 启动器或更新器在 C。
- 游戏库在其他盘，但 Xbox/Store metadata 在 C。

判断时要区分：

- program files：软件本体
- app data：用户数据
- cache：可再生缓存
- installer cache：安装/修复用缓存
- package metadata：Store/系统管理信息

### 21.3 AppData 为什么不能全迁

因为 AppData 不是单纯“缓存目录”，而是 Windows 用户配置、应用数据库、加密状态、登录态、更新器、UWP 数据的混合体。正确方法是对里面的大项逐个分类，而不是整体搬。

### 21.4 C 盘越扩越大，是否应该重装系统

如果出现以下情况，重装可能比修更省时间：

- 多年系统，安装/卸载记录严重损坏。
- `C:\Windows\Installer` 大量软件无法识别且无法修复。
- AppData 中历史残留极多。
- 多个包管理器和开发环境混乱。
- Windows Update / Store / MSI 服务反复损坏。

但重装后必须立刻设好：

- 下载目录
- Scoop root
- npm/pip/uv/pnpm/NuGet/Rust/HF/Torch caches
- 游戏库
- AI 模型目录
- Store 新应用位置
- Storage Sense

否则几个月后 C 盘会再次膨胀。

---

## 22. 新机器初始化建议

新 Win11 机器建议按这个顺序做：

1. Windows Update 完成。
2. 创建目录：

```powershell
New-Item -ItemType Directory -Force -Path `
  'D:\Software',
  'D:\Tools',
  'E:\DevTools',
  'E:\DevTools\Caches',
  'F:\File\Download',
  'F:\File\Backup',
  'F:\File\Quarantine',
  'W:\Models',
  'W:\Caches'
```

3. 设置下载目录到 `F:\File\Download`。
4. 设置 Store 新应用保存位置。
5. 安装 Scoop 到非 C 盘。
6. 配置 winget settings。
7. 配置开发缓存环境变量。
8. 安装浏览器和常用软件。
9. 安装 IDE 和 SDK 到 D/E。
10. 设置 Steam/Epic/Xbox 游戏库。
11. 开启 Storage Sense。
12. 建立每月 C 盘体检脚本。

---

## 23. 官方/权威参考

- Microsoft: [Missing Windows Installer cache requires a computer rebuild](https://learn.microsoft.com/en-us/troubleshoot/windows-client/application-management/missing-windows-installer-cache)
- Microsoft: [DISM operating system package servicing command-line options](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/dism-operating-system-package-servicing-command-line-options)
- Microsoft: [Disable and re-enable hibernation on a Windows computer](https://learn.microsoft.com/en-us/troubleshoot/windows-client/setup-upgrade-and-drivers/disable-and-re-enable-hibernation)
- Microsoft: [winget settings](https://learn.microsoft.com/en-us/windows/package-manager/winget/settings)
- Microsoft: [winget upgrade command](https://learn.microsoft.com/en-us/windows/package-manager/winget/upgrade)
- Scoop: [Scoop commands wiki](https://github.com/ScoopInstaller/Scoop/wiki/Commands)
- npm: [npm cache](https://docs.npmjs.com/cli/commands/npm-cache)
- pip: [pip cache](https://pip.pypa.io/en/stable/cli/pip_cache/)
- NuGet: [Managing the global packages, cache, and temp folders](https://learn.microsoft.com/en-us/nuget/consume-packages/managing-the-global-packages-and-cache-folders)
- Playwright: [Browsers](https://playwright.dev/docs/browsers)
- Hugging Face: [Environment variables](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables)

---

## 24. 最终结论

Win11 C 盘治理不是“删垃圾”，而是建立边界：

- 系统目录用官方工具。
- 安装器缓存不手删。
- AppData 不整体搬。
- 缓存和下载迁出去。
- 开发/AI/游戏大头从一开始就放到非 C 盘。
- 对会复发的目录做配置或自动化。
- 对不明目录先报告、备份、隔离，再删除。

如果只记一句话：  
**C 盘只放系统和必须留在用户 Profile 的状态；可再生成缓存、下载、大模型、游戏、开发工具链都应该有明确的非 C 盘归宿。**
