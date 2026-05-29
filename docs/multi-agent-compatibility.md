# Multi-Agent Compatibility

The skill pack avoids product-specific assumptions in its main instructions.

## Codex

- Use `skills/win11-storage-governance/SKILL.md`.
- Optional UI metadata is in `agents/openai.yaml`.
- Install with `scripts/install.ps1`.

## Other Agents

Agents that support Markdown skill folders can read:

- `SKILL.md`
- `references/safety-model.md`
- `references/runbook.md`
- `references/device-profile-template.md`

If the agent has no skill mechanism, use `docs/windows-11-c-drive-governance.md` as a normal runbook.

## Safety

Any agent using this pack should preserve the privacy boundary: template-only by default, local audit only on explicit request.
