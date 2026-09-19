"""Offline regression checks; no desktop session or package changes required."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

SOURCE = Path(__file__).resolve().parents[1]

class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dotfiles-config-')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home/'.config'), XDG_STATE_HOME=str(self.home/'.local/state'))

    def test_inspection_does_not_create_bootstrap_files(self):
        bindir = self.home/'bin'; bindir.mkdir()
        stub = bindir/'chezmoi'; stub.write_text('#!/bin/sh\nexit 0\n'); stub.chmod(0o755)
        for mode in ('--diff', '--verify'):
            result = subprocess.run(['bash', str(SOURCE/'install.sh'), mode], env=dict(self.env, PATH=str(bindir)+':/usr/bin:/bin'), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((self.home/'.config').exists())
            self.assertFalse((self.home/'.local').exists())

    def test_profile_is_quiet_and_idempotent(self):
        script = '. "$1"; . "$1"; printf "%s\\n%s\\n" "$PATH" "$INIR_VENV"'
        result = subprocess.run(['sh', '-c', script, 'test', str(SOURCE/'dot_profile')], env=dict(self.env, PATH='/usr/bin:/bin'), capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].split(':').count(str(self.home/'.local/bin')), 1)
        self.assertEqual(lines[1], str(self.home/'.local/state/quickshell/.venv'))

    def test_bootstrap_quotes_source_directory_in_toml(self):
        source = self.home / 'repo "quoted" \\ spaced'
        source.mkdir()
        shutil.copy2(SOURCE/'install.sh', source/'install.sh')
        bindir = self.home/'bin'; bindir.mkdir()
        real_chezmoi = shutil.which('chezmoi')
        stub = bindir/'chezmoi'
        stub.write_text('#!/usr/bin/python3\nimport os,sys\n'
                        'if sys.argv[1] == "execute-template":\n'
                        f'    os.execv({real_chezmoi!r}, [{real_chezmoi!r}, *sys.argv[1:]])\n')
        stub.chmod(0o755)
        runtime = self.home/'.config/quickshell/inir'; runtime.mkdir(parents=True)
        (runtime/'shell.qml').touch()
        subprocess.run(['bash', str(source/'install.sh')],
                       env=dict(self.env, PATH=str(bindir)+':/usr/bin:/bin'),
                       check=True, capture_output=True, text=True)
        config = tomllib.loads((self.home/'.config/chezmoi/chezmoi.toml').read_text())
        self.assertEqual(config['sourceDir'], str(source))

    def test_restore_preserves_private_modes(self):
        source = self.home/'source'
        shutil.copytree(SOURCE, source, ignore=shutil.ignore_patterns('.git', '__pycache__', '.chezmoiexternal.toml'))
        config = self.home/'chezmoi.toml'
        config.write_text('sourceDir = ' + json.dumps(str(source)) + '\n')
        destination = self.home/'destination'; destination.mkdir()
        subprocess.run(['chezmoi', '--config', str(config), '--destination', str(destination),
                        '--persistent-state', str(self.home/'state.boltdb'),
                        '--cache', str(self.home/'cache'), 'apply', '--exclude', 'scripts'],
                       check=True, capture_output=True, text=True)
        self.assertEqual((destination/'.local').stat().st_mode & 0o777, 0o700)
        self.assertEqual((destination/'.config/easyeffects/db/equalizerrc').stat().st_mode & 0o777, 0o600)
        self.assertFalse((destination/'.local/.keep').exists())

    def test_kde_wrapper_rejects_missing_variant_without_hanging(self):
        state = self.home/'.local/state/quickshell/user/generated'; state.mkdir(parents=True)
        (state/'color.txt').write_text('#aabbcc\n')
        script = SOURCE/'dot_config/matugen/templates/kde/executable_kde-material-you-colors-wrapper.sh'
        result = subprocess.run(['bash', str(script), '--scheme-variant'], env=self.env, capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('requires a value', result.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node.js is required for calculator regression checks')
    def test_calculator_exponents_and_invalid_input(self):
        qml = (SOURCE/'dot_config/quickshell/inir/modules/sidebarRight/calculator/CalculatorWidget.qml').read_text()
        code = qml[qml.index('    function calculate()'):qml.index('    function clear()')]
        harness = '''let displayValue, expression, newNumber;
function addToHistory() {}
''' + code + '''
for (const [expr, value, expected] of [
    ["", "1e-7", "1e-7"], ["1e+21 + ", "1e+21", "2e+21"],
    ["2 * ", "-3", "-6"], ["1 + ", "2 * 3", "7"],
    ["", "Error", "Error"], ["", "1foo2", "Error"],
    ["1 / ", "0", "Error"], ["", "NaN", "Error"]
]) {
    expression = expr; displayValue = value; calculate();
    if (displayValue !== expected) throw new Error(`${expr}${value}: ${displayValue} != ${expected}`);
}
'''
        subprocess.run(['node', '-e', harness], check=True, capture_output=True, text=True)

    def test_wallpapers_target_focused_monitor(self):
        # Use an output name with a quote to catch accidental jq-code interpolation.
        monitor = 'DP-"2'
        bindir = self.home/'bin'; bindir.mkdir()
        fixtures = {'niri': '#!/bin/sh\ncase "$*" in\n*focused-output*) echo \'{"name":"DP-\\"2"}\';;\n*-j*workspaces*) echo \'[{"output":"DP-\\"2","idx":4},{"output":"DP-\\"2","idx":2}]\';;\nesac\n',
                    'hyprctl': '#!/bin/sh\nexit 1\n'}
        for name, code in fixtures.items():
            p=bindir/name; p.write_text(code); p.chmod(0o755)
        for p in (SOURCE/'dot_config/quickshell/inir/scripts/colors/random').glob('*.sh'):
            text=p.read_text(); tail=text[text.index('# Check if multi-monitor'):]
            scripts=self.home/p.stem; scripts.mkdir()
            switch=scripts/'switchwall.sh'
            switch.write_text('#!/usr/bin/python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n'); switch.chmod(0o755)
            random=scripts/'random'; random.mkdir()
            config=self.home/'config.json'; config.write_text('{"background":{"multiMonitor":{"enable":true}}}')
            env=dict(self.env, PATH=str(bindir)+':/usr/bin:/bin', SCRIPT_DIR=str(random), downloadPath='/tmp/wallpaper.png', illogicalImpulseConfigPath=str(config))
            result=subprocess.run(['bash','-c',tail], env=env, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout), ['--image','/tmp/wallpaper.png','--monitor',monitor,'--start-workspace','2','--end-workspace','4'])

if __name__ == '__main__':
    unittest.main()
