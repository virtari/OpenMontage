"""Dependency-free CLI checks; never invoke a real installer or renderer."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import render_demo


class DemoCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        self.root = Path(self.temp.name)
        self.props = self.root / "props"
        self.props.mkdir()
        self.output = self.root / "renders"
        for name in ("alpha", "beta"):
            (self.props / f"{name}.json").write_text(
                json.dumps({"cuts": [{"type": "title"}]}), encoding="utf-8"
            )
        stack.enter_context(patch.object(render_demo, "PROPS_DIR", self.props))
        stack.enter_context(patch.object(render_demo, "OUTPUT_DIR", self.output))
        stack.enter_context(patch.object(
            render_demo.subprocess, "run", side_effect=AssertionError("unexpected process")
        ))

    def run_preview(self, *args):
        output = io.StringIO()
        with patch.object(render_demo, "ensure_demo_environment", side_effect=AssertionError("unexpected setup")):
            with contextlib.redirect_stdout(output):
                self.assertEqual(render_demo.main(list(args)), 0)
        self.assertFalse(self.output.exists())
        return output.getvalue()

    def test_dry_run_previews_only_selected_demo_without_setup_or_writes(self):
        output = self.run_preview("--dry-run", "alpha")
        self.assertIn(str(self.props / "alpha.json"), output)
        self.assertIn(str(self.output / "alpha.mp4"), output)
        self.assertNotIn("beta", output)

    def test_dry_run_previews_all_demos_when_name_is_omitted(self):
        output = self.run_preview("--dry-run")
        for name in ("alpha", "beta"):
            self.assertIn(str(self.props / f"{name}.json"), output)
            self.assertIn(str(self.output / f"{name}.mp4"), output)

    def test_dry_run_shows_absolute_output_directory_without_creating_it(self):
        destination = self.root / "custom output"
        output = self.run_preview("--dry-run", "alpha", "--output-dir", str(destination))
        self.assertIn(str(destination / "alpha.mp4"), output)
        self.assertFalse(destination.exists())

    def test_relative_output_directory_is_based_on_command_working_directory(self):
        with patch("os.getcwd", return_value=str(self.root)):
            output = self.run_preview("--dry-run", "alpha", "--output-dir", "relative output")
        self.assertIn(str(self.root / "relative output" / "alpha.mp4"), output)
        self.assertFalse((self.root / "relative output").exists())

    def test_list_does_not_create_custom_output_directory(self):
        destination = self.root / "list output"
        output = self.run_preview("--list", "--output-dir", str(destination))
        self.assertIn("alpha", output)
        self.assertFalse(destination.exists())

    def test_existing_file_as_output_directory_fails_before_setup(self):
        destination = self.root / "keep.mp4"
        destination.write_bytes(b"existing user file")
        for args in (["alpha"], ["--dry-run", "alpha"]):
            with self.subTest(args=args):
                with self.assertRaisesRegex(SystemExit, "not a directory"):
                    self.run_preview(*args, "--output-dir", str(destination))
                self.assertEqual(destination.read_bytes(), b"existing user file")
        self.assertFalse(self.output.exists())

    def test_render_creates_the_selected_nested_output_directory(self):
        destination = self.root / "new dir" / "out"
        with patch.object(render_demo, "ensure_demo_environment", return_value="npx"):
            with patch.object(render_demo.subprocess, "run", return_value=None):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(render_demo.main(["alpha", "--output-dir", str(destination)]), 0)
        self.assertTrue(destination.is_dir())
        self.assertFalse(self.output.exists())

    def test_render_passes_spaced_output_as_one_argument_and_keeps_existing_files(self):
        destination = self.root / "render output"
        destination.mkdir()
        existing = destination / "keep.mp4"
        existing.write_bytes(b"existing user file")
        calls = []
        with patch.object(render_demo, "ensure_demo_environment", return_value="npx"):
            with patch.object(render_demo.subprocess, "run", side_effect=lambda args, **kwargs: calls.append((args, kwargs))):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(render_demo.main(["alpha", "--output-dir", str(destination)]), 0)
        self.assertEqual(len(calls), 1)
        command, kwargs = calls[0]
        self.assertIsInstance(command, list)
        self.assertEqual(command[5], str(destination / "alpha.mp4"))
        self.assertEqual(kwargs, {"cwd": render_demo.COMPOSER_DIR, "check": True})
        self.assertEqual(existing.read_bytes(), b"existing user file")
        self.assertFalse(self.output.exists())

    def test_dry_run_rejects_invalid_props_before_setup(self):
        (self.props / "alpha.json").write_text('{"cuts": []}', encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "at least one cut"):
            self.run_preview("--dry-run", "alpha")
        self.assertFalse(self.output.exists())

    def test_dry_run_rejects_unknown_demo_before_setup(self):
        for args in (["missing"], ["--dry-run", "missing"]):
            with self.subTest(args=args):
                before = sorted(self.root.rglob("*"))
                with patch.object(render_demo, "render_demo", side_effect=AssertionError("unexpected render")):
                    with self.assertRaises(SystemExit) as result:
                        self.run_preview(*args)
                self.assertFalse(self.output.exists())
                self.assertEqual(sorted(self.root.rglob("*")), before)
                self.assertEqual(
                    result.exception.code,
                    "Unknown demo 'missing'. Available demos: alpha, beta\n"
                    "Run 'python3 render_demo.py --list' to see available demos.",
                )

    def test_list_still_avoids_setup_and_output_creation(self):
        output = self.run_preview("--list")
        self.assertIn("alpha", output)
        self.assertIn("beta", output)

    def test_help_still_exits_successfully_without_setup(self):
        with self.assertRaises(SystemExit) as result:
            self.run_preview("--help")
        self.assertEqual(result.exception.code, 0)

    def test_render_path_still_selects_named_demo(self):
        # Keep real demo discovery and selection; replace setup and rendering.
        calls = []
        with patch.object(render_demo, "ensure_demo_environment", return_value="npx"):
            with patch.object(render_demo, "render_demo", side_effect=lambda *args: calls.append(args)):
                self.assertEqual(render_demo.main(["beta"]), 0)
        self.assertEqual(calls, [("beta", self.props / "beta.json", "npx", self.output)])


class DemoCliSubprocessTests(unittest.TestCase):
    def test_help_exits_without_changing_fixture_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "render_demo.py"
            shutil.copyfile(Path(render_demo.__file__).resolve(), script)
            composer = root / "remotion-composer"
            props = composer / "public" / "demo-props"
            props.mkdir(parents=True)
            (props / "alpha.json").write_text(
                json.dumps({"cuts": [{"type": "title"}]}), encoding="utf-8"
            )

            def snapshot():
                return {
                    path.relative_to(root).as_posix(): (
                        path.read_bytes() if path.is_file() else None
                    )
                    for path in root.rglob("*")
                }

            before = snapshot()
            result = subprocess.run(
                [str(Path(sys.executable).resolve()), "-B", str(script), "--help"],
                cwd=root,
                env={"PATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("usage:", result.stdout.lower())
            self.assertIn("--help", result.stdout)
            self.assertEqual(result.stderr, "")
            self.assertFalse((root / "projects" / "demos" / "renders").exists())
            self.assertFalse((composer / "node_modules").exists())
            self.assertEqual(snapshot(), before)

    def test_unknown_demo_exits_without_changing_fixture_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "render_demo.py"
            shutil.copyfile(Path(render_demo.__file__).resolve(), script)
            composer = root / "remotion-composer"
            props = composer / "public" / "demo-props"
            props.mkdir(parents=True)
            for name in ("alpha", "beta"):
                (props / f"{name}.json").write_text(
                    json.dumps({"cuts": [{"type": "title"}]}), encoding="utf-8"
                )

            def snapshot():
                return {
                    path.relative_to(root).as_posix(): (
                        path.read_bytes() if path.is_file() else None
                    )
                    for path in root.rglob("*")
                }

            before = snapshot()
            for args in (["missing"], ["--dry-run", "missing"]):
                with self.subTest(args=args):
                    result = subprocess.run(
                        [str(Path(sys.executable).resolve()), "-B", str(script), *args],
                        cwd=root,
                        env={"PATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(
                        result.stderr,
                        "Unknown demo 'missing'. Available demos: alpha, beta\n"
                        "Run 'python3 render_demo.py --list' to see available demos.\n",
                    )
                    self.assertFalse((root / "projects" / "demos" / "renders").exists())
                    self.assertFalse((composer / "node_modules").exists())
                    self.assertEqual(snapshot(), before)
                    self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
