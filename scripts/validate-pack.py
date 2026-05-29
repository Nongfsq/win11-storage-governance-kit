from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "VERSION",
    "LICENSE",
    "CHANGELOG.md",
    "skill-pack.json",
    "docs/windows-11-c-drive-governance.md",
    "skills/win11-storage-governance/SKILL.md",
    "skills/win11-storage-governance/references/safety-model.md",
    "skills/win11-storage-governance/references/runbook.md",
    "skills/win11-storage-governance/references/device-profile-template.md",
    "skills/win11-storage-governance/agents/openai.yaml",
    "scripts/install.ps1",
    "examples/dry-runs.md",
]

FORBIDDEN_PATTERNS = [
    r"C:\\Users\\(?!<User>|Public\b)[A-Za-z0-9._-]+",
    r"[A-Z]:\\Project\\[^\\\r\n]+",
    r"AppData\\Local\\Packages\\Microsoft\.DesktopAppInstaller_8wekyb3d8bbwe",
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"20\d{6}-\d{6}",
]


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"Missing required file: {rel}")

    manifest_path = root / "skill-pack.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("name") != "win11-storage-governance-kit":
                errors.append("skill-pack.json has unexpected name")
            if not manifest.get("skills"):
                errors.append("skill-pack.json has no skills")
        except Exception as exc:
            errors.append(f"skill-pack.json is invalid JSON: {exc}")

    skill_path = root / "skills/win11-storage-governance/SKILL.md"
    if skill_path.exists():
        text = skill_path.read_text(encoding="utf-8")
        if "name: win11-storage-governance" not in text:
            errors.append("SKILL.md missing expected skill name")
        if "[TODO" in text:
            errors.append("SKILL.md still contains TODO placeholders")
        if len(text.splitlines()) > 220:
            errors.append("SKILL.md is too long; move detail into references")

    scan_files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.relative_to(root).as_posix() != "scripts/validate-pack.py"
        and path.suffix.lower() in {".md", ".json", ".ps1", ".py", ".yaml", ".yml", ".txt"}
    ]

    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(f"Potential private detail in {path.relative_to(root)}: {pattern}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: validated {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
