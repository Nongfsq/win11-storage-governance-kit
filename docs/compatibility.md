# Compatibility

## Supported Environment

- Windows 11 devices.
- Codex-style skills using `SKILL.md` frontmatter.
- PowerShell examples for Windows operations.

## Agent Compatibility

The skill is intentionally portable:

- Core instructions are in `SKILL.md`.
- Detailed references are Markdown files.
- No Codex-only tool is required to understand the workflow.

Codex-specific UI metadata is stored in `skills/win11-storage-governance/agents/openai.yaml`.

## Execution Boundary

The kit can produce plans without inspecting a machine. Local audits and cleanup require explicit user request.
