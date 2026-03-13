import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path("/a0/usr/workdir/Ea0/initialize.py")


def load_module():
    spec = importlib.util.spec_from_file_location("ea0_initialize_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class InitializePatchTest(unittest.TestCase):
    def test_patch_agent_settings_includes_usr_agents(self):
        module = load_module()
        original = """from . import files, dotenv

def convert_out(settings: Settings) -> SettingsOutput:
    out = SettingsOutput(
        settings = settings.copy(),
        additional = SettingsOutputAdditional(
            agent_subdirs=[{"value": subdir, "label": subdir}
                for subdir in files.get_subdirectories("agents")
                if subdir != "_example"],
        ),
    )
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "settings.py"
            path.write_text(original, encoding="utf-8")

            module._patch_agent_settings(path)

            patched = path.read_text(encoding="utf-8")
            self.assertIn("def _ea0_agent_subdir_options()", patched)
            self.assertIn('for root in ("agents", "usr/agents")', patched)
            self.assertIn("agent_subdirs=_ea0_agent_subdir_options()", patched)

    def test_patch_agent_settings_is_idempotent(self):
        module = load_module()
        original = """from . import files, dotenv

def convert_out(settings: Settings) -> SettingsOutput:
    out = SettingsOutput(
        settings = settings.copy(),
        additional = SettingsOutputAdditional(
            agent_subdirs=[{"value": subdir, "label": subdir}
                for subdir in files.get_subdirectories("agents")
                if subdir != "_example"],
        ),
    )
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "settings.py"
            path.write_text(original, encoding="utf-8")

            module._patch_agent_settings(path)
            once = path.read_text(encoding="utf-8")
            module._patch_agent_settings(path)
            twice = path.read_text(encoding="utf-8")

            self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
