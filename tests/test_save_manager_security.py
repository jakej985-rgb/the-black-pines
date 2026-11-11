"""
Unit tests for SaveManager security path validation logic.
Protects against path traversal attacks, directory escaping, and unauthorized writes.
"""

import unittest
from pathlib import Path


def is_valid_save_path(path: str) -> bool:
    """Python reference implementation replicating SaveManager.is_valid_save_path()."""
    if not path.startswith("user://"):
        return False
    if ".." in path or "\\" in path:
        return False
    if not path.endswith(".json"):
        return False
    return True


class TestSaveManagerSecurity(unittest.TestCase):
    def test_valid_save_paths(self):
        self.assertTrue(is_valid_save_path("user://black_pines_save.json"))
        self.assertTrue(is_valid_save_path("user://save_slot_1.json"))
        self.assertTrue(is_valid_save_path("user://backup/save_2026.json"))

    def test_reject_directory_traversal(self):
        self.assertFalse(is_valid_save_path("user://../etc/passwd.json"))
        self.assertFalse(is_valid_save_path("user://saves/../../secret.json"))
        self.assertFalse(is_valid_save_path("user://..\\windows\\win.ini.json"))

    def test_reject_unauthorized_prefixes(self):
        self.assertFalse(is_valid_save_path("res://scripts/systems/save_manager.gd"))
        self.assertFalse(is_valid_save_path("/etc/shadow.json"))
        self.assertFalse(is_valid_save_path("C:\\Users\\save.json"))
        self.assertFalse(is_valid_save_path("file:///var/tmp/save.json"))

    def test_reject_invalid_extensions(self):
        self.assertFalse(is_valid_save_path("user://save_data.exe"))
        self.assertFalse(is_valid_save_path("user://save_data.gd"))
        self.assertFalse(is_valid_save_path("user://save_data.json.bak"))
        self.assertFalse(is_valid_save_path("user://save_data"))

    def test_gdscript_implementation_matches(self):
        """Verify that the GDScript file contains the security check and expected guards."""
        save_manager_file = Path("scripts/systems/save_manager.gd")
        self.assertTrue(save_manager_file.exists(), "save_manager.gd must exist")

        content = save_manager_file.read_text(encoding="utf-8")
        self.assertIn("static func is_valid_save_path(path: String) -> bool:", content)
        self.assertIn('not path.begins_with("user://")', content)
        self.assertIn('".." in path', content)
        self.assertIn('not path.ends_with(".json")', content)
        self.assertIn("if not is_valid_save_path(path):", content)


if __name__ == "__main__":
    unittest.main()
