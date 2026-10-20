import base64
import tempfile
import unittest
from pathlib import Path

from automation.learning.secret_guard import find_secret_leaks


class SecretGuardTest(unittest.TestCase):
    def test_detects_plain_base64_and_hex_secret_without_echoing_it(self):
        secret = "meta-secret-123456"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "plain.txt").write_text("token=" + secret, encoding="utf-8")
            (root / "b64.txt").write_text(base64.b64encode(secret.encode()).decode(), encoding="utf-8")
            (root / "hex.txt").write_text(secret.encode().hex(), encoding="utf-8")
            leaks = find_secret_leaks(secret, [root])
        self.assertEqual({Path(x).name for x in leaks}, {"plain.txt", "b64.txt", "hex.txt"})
        self.assertNotIn(secret, " ".join(str(x) for x in leaks))

    def test_clean_files_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "safe.md").write_text("normal learning output", encoding="utf-8")
            self.assertEqual(find_secret_leaks("meta-secret-123456", [root]), [])

    def test_empty_secret_is_rejected(self):
        with self.assertRaises(ValueError):
            find_secret_leaks("", [Path(".")])


if __name__ == "__main__":
    unittest.main()
