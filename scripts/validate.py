#!/usr/bin/env python3
"""Offline source checks and an isolated restore; never apply to the real home."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
import xml.etree.ElementTree as ET

SOURCE = Path(__file__).resolve().parents[1]

def run(args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stdout}{result.stderr}')
    return result.stdout

def main():
    qmlformat = shutil.which('qmlformat') or '/usr/lib/qt6/bin/qmlformat'
    required = ['chezmoi', 'niri', 'fish', 'bash', 'glslangValidator']
    missing = [name for name in required if not shutil.which(name)]
    if missing or not Path(qmlformat).is_file():
        raise SystemExit('Install required tools: chezmoi niri fish bash glslang qt6-declarative')
    counts = {}
    for p in sorted(SOURCE.rglob('*')):
        if not p.is_file() or any(x in p.relative_to(SOURCE).parts for x in ['.git', '__pycache__']):
            continue
        suffix = p.suffix
        if suffix == '.qml':
            run([qmlformat, str(p)])
        elif suffix in ['.json', '.jsonc']:
            # This repo's JSONC currently uses strict JSON; reject unexpected syntax.
            json.loads(p.read_text())
        elif suffix == '.toml':
            tomllib.loads(p.read_text())
        elif suffix == '.svg' or p.name == 'fonts.conf':
            ET.parse(p)
        elif suffix == '.fish':
            run(['fish', '-n', str(p)])
        elif suffix == '.sh' or p.name in ['dot_bashrc', 'dot_bash_profile', 'dot_profile', 'dot_zprofile']:
            run(['bash', '-n', str(p)])
        elif suffix in ['.frag', '.vert']:
            run(['glslangValidator', str(p)])
        else:
            continue
        counts[suffix or 'shell profiles'] = counts.get(suffix or 'shell profiles', 0) + 1
    for p in [SOURCE/'README.md', *sorted((SOURCE/'docs').glob('*.md')), SOURCE/'THIRD_PARTY.md']:
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if re.match(r'[a-z]+:', target) or target.startswith('#'):
                continue
            if not (p.parent / target.split('#')[0]).exists():
                raise RuntimeError(f'Broken local link in {p.relative_to(SOURCE)}: {target}')
    with tempfile.TemporaryDirectory(prefix='dotfiles-validate-') as tmp:
        root = Path(tmp); staged = root/'source'; home = root/'home'; home.mkdir()
        shutil.copytree(SOURCE, staged, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        # Font payloads are checksummed separately; restore validation stays offline.
        (staged/'.chezmoiexternal.toml').unlink()
        config = root/'chezmoi.toml'
        config.write_text('sourceDir = ' + json.dumps(str(staged)) + '\n')
        base = ['chezmoi', '--config', str(config), '--destination', str(home),
                '--persistent-state', str(root/'state.boltdb'), '--cache', str(root/'cache')]
        run(base + ['apply', '--exclude', 'scripts'])
        run(base + ['verify', '--exclude', 'scripts'])
        run(['niri', 'validate', '-c', str(home/'.config/niri/config.kdl')])
        for p in home.rglob('*.json'):
            json.loads(p.read_text())
        for name in ['version', 'version.json', 'migrations.json']:
            assert not (home/'.config/inir'/name).exists(), name
        for name in ['docs', 'assets', 'scripts', 'tests', 'LICENSES', '.github', 'THIRD_PARTY.md']:
            assert not (home/name).exists(), f'Repository-only path deployed: {name}'
        assert (home/'.config/kitty/current-theme.conf').resolve().is_file()
        assert (home/'.local').stat().st_mode & 0o777 == 0o700
        assert (home/'.config/easyeffects/db/equalizerrc').stat().st_mode & 0o777 == 0o600
    print('Source syntax:', json.dumps(counts, sort_keys=True))
    print('PASS: local documentation links, offline restore/verify, rendered JSON and Niri, private modes and exclusions')

if __name__ == '__main__':
    main()
