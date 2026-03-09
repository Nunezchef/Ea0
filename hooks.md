# Runtime Hooks

This plugin maps EA0 hook semantics into Agent0 extension points and executes configured EA0 hook commands via:

- `python/helpers/ea0_sync/transform_hooks.py`
- `python/helpers/ea0_sync/hook_runtime.py`

Installed hook bridge files are generated under:

- `usr/extensions/agent_init/_80_ea0_*.py`
- `usr/extensions/tool_execute_before/_80_ea0_*.py`
- `usr/extensions/tool_execute_after/_80_ea0_*.py`
- `usr/extensions/message_loop_end/_80_ea0_*.py`
- `usr/extensions/message_loop_prompts_before/_80_ea0_*.py`
