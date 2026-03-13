# Everything Agent0 (Ea0)

Ea0 is a **plugin-only integration layer** that ports Everything Claude Code (EA0) into Agent0.

It does not ship a fork of Agent0.  
It installs a runtime transformer pipeline that:
- pulls EA0 content from `usr/everything-claude-code`
- transforms it into Agent0-compatible layout
- injects EA0 workflow guidance into Agent0 system prompt
- maps EA0 hooks/events into Agent0 extension points
- provides UI controls for sync, update, backup, restore

## Scope

Ea0 integrates the EA0 ecosystem into Agent0 in six domains:
- Skills
- Agents
- Command knowledge
- Hook bridges
- Ecosystem tools/scripts
- Core memory + system prompt context

## Architecture

Ea0 runtime consists of:
- API: `python/api/ea0_sync.py`
- Tool: `python/tools/ea0_sync_tool.py`
- Transformers: `python/helpers/ea0_sync/*.py`
- UI panel: `webui/components/settings/ea0/*`
- Prompt injection: `usr/extensions/system_prompt/_50_ea0_context.py`

### Transformation model

Ea0 does not use EA0 files in-place inside Agent0 runtime. It transforms and writes generated outputs into `usr/*` and state under `usr/plugins/ea0-integration/state/*`.

Primary flow:
1. Resolve EA0 vendor root (`usr/everything-claude-code`)
2. Transform EA0 domains into Agent0 targets
3. Write manifest/vendor state
4. Remove stale previously-generated files
5. Promote staged outputs into workspace
6. Recompute health report

## EA0 -> Agent0 Mapping

| EA0 domain | Agent0 output |
|---|---|
| skills | `usr/skills/ea0/*` |
| agents | `usr/agents/ea0/*` |
| command docs | `usr/knowledge/ea0-commands/*` |
| contexts | `usr/knowledge/core-memories/ea0/*` |
| scripts/tools | `usr/plugins/ea0-integration/tools/*` |
| hook config/events | `usr/extensions/*/_80_ea0_*.py` |

## Hook Integration

EA0 event semantics are bridged into Agent0 extension points:

| EA0 event | Agent0 extension point |
|---|---|
| `SessionStart` | `agent_init` |
| `PreToolUse` | `tool_execute_before` |
| `PostToolUse` | `tool_execute_after` |
| `PreCompact` | `message_loop_prompts_before` |
| `SessionEnd` | `message_loop_end` |
| `Stop` | `message_loop_end` |

Hook command execution is handled by:
- `python/helpers/ea0_sync/hook_runtime.py`

Safety guarantees:
- non-JSON payload objects are normalized before serialization
- command timeout guard is enforced
- failures are isolated to hook result payload (non-fatal to core flow)

## System Prompt / Memory Integration

Ea0 follows the same pattern used by framework-style prompt integrations:

1. `usr/extensions/system_prompt/_50_ea0_context.py` appends EA0 context each run
2. primary source: `usr/prompts/fw.ea0.reference.md`
3. fallback source: `usr/knowledge/core-memories/ea0/agent0-ea0-integration.md`

This ensures Agent0 explicitly knows EA0 is active and can prioritize EA0 capabilities during execution.

## Settings UI Integration

Ea0 adds:
- `Settings -> External Services -> EA0 Integration`

Panel capabilities:
- `Install / Sync EA0`
- `Update Latest (Git)`
- `Create Backup Point`
- `Restore Backup`

Panel status fields:
- health status
- EA0 git repository URL
- current vendor SHA
- installed/synced SHA
- last sync timestamp
- injection status flags (extension/prompt/core-memory)

## API Actions

Endpoint: `/ea0_sync`

Supported actions:
- `status`
- `sync`
- `update_latest`
- `backup_create`
- `backup_list`
- `backup_restore`

## Quick Install (Copy/Paste)

Use this exact flow on a fresh Agent0 instance:

```bash
cd /a0/usr/workdir
rm -rf .a0-install
git clone --branch main https://github.com/Nunezchef/Ea0.git .a0-install
bash /a0/usr/workdir/.a0-install/install.sh /a0
```

Then restart Agent0.

If your Agent0 root is not `/a0`, replace the final argument with your real Agent0 root path.

## One-Line Agent0 Prompt

If you want Agent0 to run installation for you, paste this:

```text
Install this plugin from main branch only: https://github.com/Nunezchef/Ea0.git. Clone it into /a0/usr/workdir/.a0-install and run: bash /a0/usr/workdir/.a0-install/install.sh /a0
```

## Agent0 Installation Instructions

Use this section when the installer is being executed by Agent0 itself.

Agent0 should follow this exact behavior:

1. remove any previous temporary install directory at `/a0/usr/workdir/.a0-install`
2. clone `https://github.com/Nunezchef/Ea0.git` from `main` into `/a0/usr/workdir/.a0-install`
3. run `bash /a0/usr/workdir/.a0-install/install.sh /a0`
4. do not run `/a0/docker/run/fs/ins/install_A0.sh`
5. after installation, report the installed commit from `/a0/usr/plugins/ea0/.installed-from-commit`
6. tell the user a full Agent0 backend restart is required

Exact Agent0 instruction:

```text
Install EA0 plugin from https://github.com/Nunezchef/Ea0.git using main branch only. Remove /a0/usr/workdir/.a0-install first if it exists, clone fresh into /a0/usr/workdir/.a0-install, run bash /a0/usr/workdir/.a0-install/install.sh /a0, do NOT run /a0/docker/run/fs/ins/install_A0.sh, then report the installed commit from /a0/usr/plugins/ea0/.installed-from-commit and tell the user a full backend restart is required.
```

## Agent0 Auto-Install Prompt (Recommended)

Use this exact prompt with Agent0 so users can install without manual troubleshooting:

```text
Install EA0 plugin from https://github.com/Nunezchef/Ea0.git (main branch only). Do a clean install: remove /a0/usr/workdir/.a0-install first, clone fresh into /a0/usr/workdir/.a0-install, run bash /a0/usr/workdir/.a0-install/install.sh /a0, and do NOT run /a0/docker/run/fs/ins/install_A0.sh. After install, verify /a0/python/api/ea0_sync.py contains clear_extensions_cache fallback and report the installed commit from /a0/usr/plugins/ea0/.installed-from-commit.
```

## Post-Install Check

After restart, verify:
1. Open `Settings -> External Services -> EA0 Integration`
2. Click `Install / Sync EA0`
3. Confirm status fields populate (health, repo URL, vendor SHA, synced SHA, last sync)
4. Confirm health is `healthy`

## Troubleshooting (Common Install Errors)

| Symptom | Cause | Fix |
|---|---|---|
| `No such file or directory: /a0/.a0-install/...` | Wrong clone path | Use `/a0/usr/workdir/.a0-install/...` |
| `Error: Branch parameter is empty` | Wrong script used (`install_A0.sh`) | Use plugin installer `install.sh` |
| `EA0 tab missing in UI` | Installer not run against live Agent0 root | Re-run installer with correct root, then restart Agent0 |
| Sync fails on vendor path | EA0 vendor root missing | Open EA0 panel and run `Install / Sync EA0` after install |

## Operational Workflows

### First-time bootstrap
1. run installer
2. restart Agent0
3. open EA0 Integration panel
4. run `Install / Sync EA0`
5. verify health = `healthy`

### Daily workflow
1. use Agent0 normally with EA0-enabled prompts/hooks
2. update when needed with `Update Latest (Git)`
3. keep `Backup Before Update` enabled for safe rollback

### Safe upgrade workflow
1. create backup point
2. update latest
3. verify injection flags and hook health
4. rollback using `Restore Backup` if required

### Disaster recovery workflow
1. reinstall Agent0 base
2. reinstall Ea0 plugin
3. re-run sync
4. restore backup point from `usr/plugins/ea0-integration/backups/` if needed

## Verification Checklist

After install/sync:
- EA0 panel appears under External Services
- `status.health_report.status == healthy`
- injection flags all active
- generated EA0 files present in `usr/skills/ea0`, `usr/agents/ea0`, `usr/knowledge/ea0-commands`
- hook bridges present under `usr/extensions/*_ea0_*.py`
- manifest exists at `usr/plugins/ea0-integration/state/manifest.json`

CLI checks:
```bash
test -f /a0/usr/plugins/ea0-integration/state/manifest.json
test -f /a0/usr/extensions/system_prompt/_50_ea0_context.py
test -f /a0/usr/prompts/fw.ea0.reference.md
test -d /a0/usr/skills/ea0
test -d /a0/usr/agents/ea0
```

## Repository Layout

- `plugin.yaml`: plugin metadata
- `hooks.md`: runtime hook behavior summary
- `install.sh`: primary community-style installer
- `initialize.py`: plugin initializer (applies runtime payload + initial EA0 sync)
- `scripts/install-into-agent0.sh`: compatibility wrapper to `install.sh`
- `runtime/python/*`: API/tool/transform runtime payload
- `runtime/webui/*`: EA0 settings UI payload
- `runtime/usr/*`: prompt/memory/system_prompt payload

## Notes

- Repo is intentionally plugin-only.
- Installer patches `webui/components/settings/external/external-settings.html` once (idempotent guard included).
- Re-run installer after Agent0 upgrades/reinstalls.
