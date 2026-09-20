#!/usr/bin/env python3
"""Online desktop package availability check; does not install packages."""
import json
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request

SOURCE = Path(__file__).resolve().parents[1]

def names(filename):
    return [line.split('#', 1)[0].strip() for line in (SOURCE/filename).read_text().splitlines()
            if line.split('#', 1)[0].strip()]

def main():
    official, aur = names('packages-repo.txt'), names('packages-aur.txt')
    personal = set(names('packages-apps.txt'))
    if personal.intersection(official + aur):
        raise SystemExit('Personal packages found in the desktop manifests')
    subprocess.run(['pacman', '-Sp', '--noconfirm', '--print-format', '%n', '--', *official],
                   check=True, stdout=subprocess.DEVNULL, timeout=120)
    query = urllib.parse.urlencode([('arg[]', name) for name in aur])
    request = urllib.request.Request('https://aur.archlinux.org/rpc/v5/info?' + query,
                                     headers={'User-Agent': 'dotfiles-package-check'})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('type') == 'error':
        raise SystemExit('AUR query failed: ' + str(result.get('error')))
    found = {package['Name'] for package in result['results']}
    if missing := set(aur) - found:
        raise SystemExit('Missing AUR packages: ' + ', '.join(sorted(missing)))
    print(f'PASS: {len(official)} official packages resolve; {len(aur)} AUR packages exist; personal apps excluded')

if __name__ == '__main__':
    main()
