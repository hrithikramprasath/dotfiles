"""Exercise the rendered restore hook without installing anything on the host."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
STUB = '''#!/usr/bin/python3
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
with open(os.environ['TEST_LOG'], 'a') as f:
    f.write(json.dumps([name, *sys.argv[1:]]) + '\\n')
if name == 'sudo':
    os.execvp(sys.argv[1], sys.argv[1:])
if name == 'git' and sys.argv[1] == 'clone':
    root = pathlib.Path(sys.argv[-1]); root.mkdir(parents=True)
    (root / 'setup').write_text('#!/bin/bash\\nrestore-runtime\\n')
if name == 'restore-runtime' and not os.environ.get('FAIL_INSTALL'):
    home = pathlib.Path.home()
    for rel in ['.config/quickshell/inir/shell.qml', '.local/bin/inir', '.local/state/quickshell/.venv/bin/python']:
        target = home / rel; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('#!/bin/sh\\nexit 0\\n'); target.chmod(0o755)
if name == os.environ.get('FAIL_COMMAND') or (name == 'restore-runtime' and os.environ.get('FAIL_INSTALL')):
    sys.exit(17)
'''

class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dotfiles-restore-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home'; self.home.mkdir()
        self.bin = self.root / 'bin'; self.bin.mkdir()
        self.source = self.root / 'source'; self.source.mkdir()
        for name in ['packages-repo.txt', 'packages-aur.txt', 'inir-revision.txt']:
            shutil.copy2(SOURCE / name, self.source / name)
        (self.source / 'packages-repo.txt').write_text('# core\nniri\n\nkitty # terminal\n')
        (self.source / 'packages-aur.txt').write_text('# theme\ndarkly-bin\n')
        self.log = self.root / 'commands.jsonl'
        for name in ['sudo', 'pacman', 'yay', 'git', 'restore-runtime']:
            p = self.bin / name; p.write_text(STUB); p.chmod(0o755)
        config = self.root / 'chezmoi.toml'
        config.write_text('sourceDir = ' + json.dumps(str(self.source)) + '\n')
        rendered = subprocess.check_output([
            shutil.which('chezmoi'), '--config', str(config), 'execute-template',
        ], input=(SOURCE / '.chezmoiscripts/run_onchange_before_install-packages.sh.tmpl').read_text(), text=True)
        self.script = self.root / 'restore.sh'; self.script.write_text(rendered)
        self.env = dict(os.environ, HOME=str(self.home), PATH=str(self.bin)+':/usr/bin:/bin', TEST_LOG=str(self.log))

    def run_hook(self, **env):
        result = subprocess.run(['bash', str(self.script)], env=dict(self.env, **env), capture_output=True, text=True)
        self.commands = [json.loads(x) for x in self.log.read_text().splitlines()] if self.log.exists() else []
        return result

    def test_fresh_install_pins_revision_and_parses_comments(self):
        result = self.run_hook(); self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(['pacman', '-S', '--needed', '--noconfirm', '--', 'niri', 'kitty'], self.commands)
        self.assertIn(['git', '-C', str(self.home/'inir'), 'checkout', '-B', 'main', (SOURCE/'inir-revision.txt').read_text().strip()], self.commands)
        self.assertTrue((self.home/'.local/bin/inir').exists())

    def test_invalid_revision_aborts_before_package_changes(self):
        (self.source / 'inir-revision.txt').write_text('invalid\n')
        result = self.run_hook()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.commands, [])

    def test_repository_failure_aborts_before_aur(self):
        result = self.run_hook(FAIL_COMMAND='pacman'); self.assertEqual(result.returncode, 17)
        self.assertFalse(any(c[0] in ['yay', 'git'] for c in self.commands))

    def test_aur_failure_aborts_before_checkout(self):
        result = self.run_hook(FAIL_COMMAND='yay'); self.assertEqual(result.returncode, 17)
        self.assertFalse(any(c[0] == 'git' for c in self.commands))

    def test_existing_checkout_with_missing_runtime_is_repaired(self):
        repo=self.home/'inir'; repo.mkdir(); (repo/'setup').write_text('restore-runtime\n')
        result=self.run_hook(); self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(['restore-runtime'], self.commands)
        self.assertFalse(any(c[0] == 'git' for c in self.commands))

    def test_installer_failure_is_not_reported_as_success(self):
        result=self.run_hook(FAIL_INSTALL='1'); self.assertEqual(result.returncode, 17)
        self.assertNotIn('completed successfully', result.stdout)

    def test_complete_install_does_not_reset_existing_checkout(self):
        subprocess.run([str(self.bin/'restore-runtime')], env=self.env, check=True)
        result=self.run_hook(); self.assertEqual(result.returncode, 0, result.stderr)
        # A complete runtime may have a missing checkout; the pinned checkout is
        # cloned, but the live installer must not run again.
        self.assertEqual(sum(c[0]=='restore-runtime' for c in self.commands), 1)

if __name__ == '__main__':
    unittest.main()
