# Windows 11 Storage Governance Kit

中文 | [English](README.md)

一套用于处理 Windows 11 系统盘臃肿问题的 Codex Skills 工具包。

这个项目把一套真实可执行的 Win11 C 盘治理方法整理成可复用的 agent skill 和参考文档。它的核心不是简单“删垃圾”，而是治理系统盘：先识别和分类，再清理低风险缓存，把会反复膨胀的大型缓存迁移到非系统盘，并用包管理器、环境变量、官方工具和自动化策略长期控制 C 盘增长。

## 它解决什么问题

Windows 11 机器经常在这些位置堆出几十 GB 甚至上百 GB：

- `%TEMP%`、`C:\Windows\Temp`、更新缓存、Delivery Optimization。
- `AppData\Local` 和 `AppData\Roaming`。
- Electron updater 残留和浏览器 Profile 缓存。
- `C:\Windows\Installer`、WinSxS、WindowsApps 等系统管理目录。
- winget、Scoop、npm、pip、NuGet、Rust、Playwright、Puppeteer、Hugging Face、Torch 缓存。
- NVIDIA/DirectX shader cache、游戏启动器、AI 模型、开发 SDK。

普通清理教程通常只告诉你删几个缓存目录。但如果没有长期的存储策略，这些内容很快会重新长回来。

这个工具包提供的就是这套策略。

## 核心原则

- **先观察，再删除。** 先找出真实的大目录。
- **按风险分类。** 缓存、应用数据、安装器缓存、系统服务目录、用户文件不能用同一种删除策略。
- **优先使用官方工具。** WinSxS、Windows Update、Store/UWP、Visual Studio、驱动、MSI 修复都不应该靠手动删文件处理。
- **迁移会复发的大头。** 开发缓存、包缓存、下载、模型、游戏库、shader cache 应该有明确的非 C 盘归宿。
- **不要整体迁移系统状态。** 不要 junction `C:\Windows\Installer`、`C:\Windows\WinSxS`、`C:\Program Files\WindowsApps`、整个用户目录、整个 `AppData` 或整个 `ProgramData`。
- **保护隐私。** skill 默认只输出模板化计划，不读取本机用户目录、注册表、环境变量、日志或包清单，除非用户明确要求本机检查。

## 仓库结构

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

## Skill

Skill 名称：

```text
win11-storage-governance
```

适合这些场景：

- Win11 C 盘空间异常膨胀。
- 分析 `AppData`、`C:\Windows\Installer`、WinSxS、WindowsApps。
- 判断 winget 和 Scoop 的分工。
- 迁移包管理器、开发工具、AI、浏览器、shader cache。
- 制作定期清理策略。
- 为单台 Win11 设备或一批类似设备制作安全清理方案。

Skill 本体保持简短，详细规则放在：

- `skills/win11-storage-governance/references/safety-model.md`
- `skills/win11-storage-governance/references/runbook.md`
- `skills/win11-storage-governance/references/device-profile-template.md`

## 安装 Codex Skill

在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

安装到指定 skills 目录：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -DestinationRoot "C:\Users\<User>\.codex\skills"
```

覆盖已有版本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Force
```

## 示例 Prompt

```text
Use $win11-storage-governance to create a safe Windows 11 C-drive cleanup and storage migration plan for a developer workstation. Do not inspect the local machine.
```

如果要做本机检查，必须明确说：

```text
Use $win11-storage-governance to inspect this Windows 11 machine and report what is safe to clean. Do not delete anything.
```

## 验证

验证项目：

```powershell
python .\scripts\validate-pack.py .
```

如果本机有 Codex 系统 skill validator，可以验证 skill：

```powershell
python C:\Users\<User>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skills\win11-storage-governance
```

如果 Python 环境缺少 `PyYAML`，可以使用隔离运行方式：

```powershell
uvx --with pyyaml python C:\Users\<User>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skills\win11-storage-governance
```

## 安全提示

这个项目默认保守。它不会建议手动删除 Windows 服务目录或安装器缓存，尤其是：

- 不要手动删除 `C:\Windows\Installer`。
- 不要手动删除 `C:\Windows\WinSxS`。
- 不要手动移动 `C:\Program Files\WindowsApps`。
- 不要整体 junction `AppData`、用户目录或 `ProgramData`。

高风险区域应使用官方工具、厂商卸载器、修复工具、隔离流程和回滚方案处理。

## 许可证

MIT License。
