from __future__ import annotations

from pathlib import Path
import shutil


def transform_core_memories(vendor_root: Path, output_root: Path) -> list[str]:
    src_base = vendor_root / "contexts"
    dst_base = output_root / "usr" / "knowledge" / "core-memories" / "ea0"
    generated: list[str] = []

    if not src_base.is_dir():
        return generated

    for src_file in sorted(src_base.rglob("*")):
        if not src_file.is_file():
            continue
        rel = src_file.relative_to(src_base)
        dst_file = dst_base / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        generated.append(str(dst_file.relative_to(output_root)).replace("\\", "/"))

    # Integration memory ensures Agent0 is explicitly aware EA0 is active and available.
    integration_memory = dst_base / "agent0-ea0-integration.md"
    integration_memory.parent.mkdir(parents=True, exist_ok=True)
    integration_memory.write_text(
        (
            "# EA0 Integration Active\n\n"
            "EA0 integration is installed and active in this Agent0 workspace.\n\n"
            "## Operating Guidance\n"
            "- Prefer EA0-provided capabilities when they help complete the user's request faster or with better quality.\n"
            "- Use EA0 skills under `usr/skills/ea0/` when a matching workflow exists.\n"
            "- Use EA0 specialist agents under `usr/agents/ea0/` for targeted review, planning, testing, and refactoring tasks.\n"
            "- Use EA0 command knowledge under `usr/knowledge/ea0-commands/` for command-oriented workflows.\n"
            "- Keep EA0 hooks and toolchain compatibility intact; do not remove generated EA0 extensions unless explicitly asked.\n\n"
            "## Safety and Scope\n"
            "- Follow user instructions and repository constraints first.\n"
            "- If EA0 behavior conflicts with explicit user direction, follow the user and explain the tradeoff briefly.\n"
        ),
        encoding="utf-8",
    )
    generated.append(str(integration_memory.relative_to(output_root)).replace("\\", "/"))

    reference_prompt = output_root / "usr" / "prompts" / "fw.ea0.reference.md"
    reference_prompt.parent.mkdir(parents=True, exist_ok=True)
    reference_prompt.write_text(
        (
            "# EA0 Workflow Integration\n\n"
            "EA0 integration is active for this Agent0 instance.\n\n"
            "Use EA0 assets proactively when they improve execution quality or speed:\n"
            "- Skills: `usr/skills/ea0/`\n"
            "- Specialist agents: `usr/agents/ea0/`\n"
            "- Command knowledge: `usr/knowledge/ea0-commands/`\n"
            "- Hook/toolchain outputs: `usr/extensions/*_ea0_*` and `usr/plugins/ea0-integration/tools/`\n\n"
            "When planning or implementing work:\n"
            "- Prefer EA0 workflows for TDD, review, verification, orchestration, and refactoring when relevant.\n"
            "- Keep EA0-generated integration assets intact unless the user explicitly requests removal.\n"
            "- Follow explicit user instructions first when they conflict with EA0 defaults.\n"
        ),
        encoding="utf-8",
    )
    generated.append(str(reference_prompt.relative_to(output_root)).replace("\\", "/"))

    context_extension = output_root / "usr" / "extensions" / "system_prompt" / "_50_ea0_context.py"
    context_extension.parent.mkdir(parents=True, exist_ok=True)
    context_extension.write_text(
        (
            "from python.helpers.extension import Extension\n"
            "from python.helpers import files\n\n\n"
            "class Ea0Context(Extension):\n"
            "    async def execute(self, system_prompt: list[str] = [], **kwargs):\n"
            "        prompt = ''\n"
            "        if self.agent:\n"
            "            try:\n"
            "                prompt = self.agent.read_prompt('fw.ea0.reference.md')\n"
            "            except Exception:\n"
            "                prompt = ''\n"
            "        if not prompt:\n"
            "            memory_path = files.get_abs_path(\n"
            "                'usr',\n"
            "                'knowledge',\n"
            "                'core-memories',\n"
            "                'ea0',\n"
            "                'agent0-ea0-integration.md',\n"
            "            )\n"
            "            if files.exists(memory_path):\n"
            "                prompt = files.read_file(memory_path)\n"
            "        if prompt:\n"
            "            system_prompt.append(prompt)\n"
        ),
        encoding="utf-8",
    )
    generated.append(str(context_extension.relative_to(output_root)).replace("\\", "/"))

    return generated
