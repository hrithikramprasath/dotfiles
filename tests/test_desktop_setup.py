"""Test post-restore failures and service ordering without touching the host."""
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
name=pathlib.Path(sys.argv[0]).name
with open(os.environ['TEST_LOG'], 'a') as f:
 f.write(json.dumps([name, *sys.argv[1:]])+'\\n')
if name == os.environ.get('FAIL_COMMAND'):
 sys.exit(17)
if name == 'sudo':
 os.execvp(sys.argv[1],sys.argv[1:])
if name == 'inir':
 p=pathlib.Path.home()/'.config/systemd/user/niri.service.wants/inir.service'
 p.parent.mkdir(parents=True,exist_ok=True)
 p.symlink_to('../inir.service')
'''

class DesktopSetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='desktop-setup-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.home=self.root/'home'; self.home.mkdir()
        self.bin=self.root/'bin'; self.bin.mkdir(); self.log=self.root/'log.jsonl'
        for name in ['sudo','systemctl','niri','qs','Xorg','gsettings','fc-cache','xdg-user-dirs-update','python','inir','theme-install']:
            p=self.bin/name;p.write_text(STUB);p.chmod(0o755)
        # Redirect only filesystem fixtures; the real shell script controls ordering.
        script=(SOURCE/'scripts/finalize-desktop.sh').read_text()
        for prefix in ['/usr/share','/etc/sddm.conf.d']:
            script=script.replace(prefix,str(self.root/prefix.lstrip('/')))
        self.script=self.root/'finalize.sh';self.script.write_text(script)
        files=['.config/quickshell/inir/shell.qml','.config/systemd/user/inir.service',
               '.local/share/color-schemes/Darkly.colors','.local/state/quickshell/user/generated/colors.json',
               'Pictures/Wallpapers/wallpaper666.png']
        for rel in files:
            p=self.home/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture\n')
        for path in [self.home/'.local/bin/inir', self.home/'.config/quickshell/inir/scripts/inir',self.home/'.local/state/quickshell/.venv/bin/python']:
            path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(self.bin/('python' if path.name=='python' else 'inir'),path)
        config=self.home/'.config/inir/config.json';config.parent.mkdir(parents=True)
        config.write_text(json.dumps({'background':{'wallpaperPath':str(self.home/'Pictures/Wallpapers/wallpaper666.png')}}))
        for rel in ['usr/share/wayland-sessions/niri.desktop','usr/share/sddm/themes/ii-pixel/Main.qml','usr/share/sddm/themes/ii-pixel/assets/background.png','etc/sddm.conf.d/99-inir-theme.conf']:
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('Current=ii-pixel\n')
        installer=self.home/'inir/scripts/sddm/install-pixel-sddm.sh';installer.parent.mkdir(parents=True)
        installer.write_text('theme-install\n')
        self.env=dict(os.environ,HOME=str(self.home),PATH=str(self.bin)+':/usr/bin:/bin',TEST_LOG=str(self.log),XDG_CONFIG_HOME=str(self.home/'.config'))

    def run_setup(self, **env):
        result=subprocess.run(['bash',str(self.script)],env=dict(self.env,**env),text=True,capture_output=True)
        self.commands=[json.loads(l) for l in self.log.read_text().splitlines()] if self.log.exists() else []
        return result

    def test_fresh_desktop_enables_next_login_without_starting_sddm(self):
        result=self.run_setup();self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(['systemctl','enable','NetworkManager.service','bluetooth.service','power-profiles-daemon.service','sddm.service'],self.commands)
        self.assertIn(['systemctl','--user','enable','pipewire.socket','pipewire-pulse.socket','wireplumber.service'],self.commands)
        self.assertTrue((self.home/'.config/systemd/user/niri.service.wants/inir.service').exists())
        self.assertFalse(any('start' in c or 'restart' in c or '--now' in c for c in self.commands))
        self.assertLess(self.commands.index(['theme-install']),self.commands.index(['systemctl','enable','NetworkManager.service','bluetooth.service','power-profiles-daemon.service','sddm.service']))

    def test_invalid_niri_config_aborts_before_theme_and_services(self):
        result=self.run_setup(FAIL_COMMAND='niri');self.assertEqual(result.returncode,17)
        self.assertFalse(any(c[0] in ['theme-install','sudo'] for c in self.commands))

    def test_theme_failure_does_not_report_success(self):
        result=self.run_setup(FAIL_COMMAND='theme-install');self.assertEqual(result.returncode,17)
        self.assertNotIn('verified',result.stdout)
        self.assertFalse(any(c[0]=='sudo' for c in self.commands))

    def test_missing_wallpaper_aborts(self):
        (self.home/'Pictures/Wallpapers/wallpaper666.png').unlink()
        result=self.run_setup();self.assertNotEqual(result.returncode,0)
        self.assertIn('missing configured wallpaper',result.stderr)

    def test_desktop_manifests_exclude_personal_apps_and_boot_choices(self):
        def packages(file):
            return {s.split('#')[0].strip() for s in (SOURCE/file).read_text().splitlines() if s.split('#')[0].strip()}
        desktop=packages('packages-repo.txt')|packages('packages-aur.txt')
        self.assertFalse(desktop & packages('packages-apps.txt'))
        self.assertFalse(desktop & {'linux','linux-lts','amd-ucode','intel-ucode','mkinitcpio','efibootmgr','snapper','ufw'})
        self.assertTrue({'sddm','xorg-server','xorg-xauth','niri','pipewire','wireplumber','networkmanager'} <= desktop)

if __name__=='__main__':
    unittest.main()
