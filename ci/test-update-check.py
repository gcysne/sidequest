#!/usr/bin/env python3
"""Tests for the update checks: bin/sidequest-update-check (session-start hook) and the plugin's _version_key.

Both must order versions the same way (semver: pre-releases before the release, alpha < beta). Runs offline.
"""
import ast
import importlib.machinery
import importlib.util
import io
import json
import os
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["0.1.0-alpha", "0.1.1-alpha", "0.2.0-alpha", "0.2.0-alpha.2", "0.2.0-alpha.10", "0.2.0-beta",
         "0.2.0-beta.1", "0.2.0-beta.2", "0.2.0", "0.2.1", "0.10.0-alpha", "1.0.0-beta.1", "1.0.0", "1.0.1"]


def load_hook():
    loader = importlib.machinery.SourceFileLoader("sidequest_update_check", str(ROOT / "bin/sidequest-update-check"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def load_plugin_key():
    """_version_key from decky-plugin/main.py without importing it (it needs Decky's `decky` module)."""
    tree = ast.parse((ROOT / "decky-plugin/main.py").read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_version_key")
    ns = {"re": __import__("re")}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "main.py", "exec"), ns)
    return ns["_version_key"]


class VersionOrder(unittest.TestCase):
    def test_order(self):
        for key in (load_hook().version_key, load_plugin_key()):
            self.assertEqual(sorted(reversed(ORDER), key=key), ORDER)
            self.assertEqual(key("v0.2.0-beta.1"), key("0.2.0-beta.1"))


class Hook(unittest.TestCase):
    def run_hook(self, installed, tags):
        mod = load_hook()
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            (home / ".local/lib/sidequest").mkdir(parents=True)
            (home / ".local/lib/sidequest/VERSION").write_text(installed + "\n")
            mod.VERSION_FILE = home / ".local/lib/sidequest/VERSION"
            mod.STATE = home / "state/update-check.json"
            body = json.dumps([{"tag_name": "v" + t, "draft": False} for t in tags]).encode()
            with mock.patch("urllib.request.urlopen", return_value=io.BytesIO(body)), redirect_stdout(io.StringIO()) as out:
                mod.main()
            cache = json.loads(mod.STATE.read_text())
            return out.getvalue(), cache

    def test_newer_prerelease_label(self):
        out, cache = self.run_hook("0.2.0-alpha", ["0.1.0-alpha", "0.2.0-beta.1", "0.2.0-alpha"])
        self.assertEqual(cache["latest"], "0.2.0-beta.1")
        self.assertIn("installed 0.2.0-alpha, latest 0.2.0-beta.1", out)

    def test_up_to_date(self):
        out, _ = self.run_hook("0.2.0", ["0.2.0", "0.2.0-beta.2"])
        self.assertEqual(out, "")

    def test_cache_used_within_a_day(self):
        mod = load_hook()
        with tempfile.TemporaryDirectory() as d:
            mod.VERSION_FILE = Path(d) / "VERSION"
            mod.VERSION_FILE.write_text("0.1.0-alpha")
            mod.STATE = Path(d) / "update-check.json"
            mod.STATE.write_text(json.dumps({"checked": time.time(), "latest": "0.1.1-alpha"}))
            with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")), \
                    redirect_stdout(io.StringIO()) as out:
                mod.main()
            self.assertIn("latest 0.1.1-alpha", out.getvalue())


if __name__ == "__main__":
    unittest.main()
