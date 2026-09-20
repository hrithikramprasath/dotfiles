# iNiR 2.31 upgrade — 20 September 2026

The live shell and the fresh-install pin now use iNiR 2.31.0, based on upstream
[`9574fa42`](https://github.com/snowarch/inir/tree/9574fa424c0d1008e927454e933a7fbe292f9fb2).
The local development checkout merged that release while retaining the existing
pill, panel, tooltip, calculator, wallpaper and Autostart customizations.

## Changes

Six overlapping files needed merge resolutions: background widgets, the widget
manager, shared panel surfaces, Japanese lookup, recording OSD and Wallhaven.
The resolutions retain the new iRiS/Editorial branches and existing custom surface
behavior. Wallhaven keeps upstream retry/parsing improvements and reports the
actual temporary provider error status instead of hard-coding HTTP 521.

A live restart revealed an upstream launcher bug: when the last optional Niri
environment variable is absent, a helper returns status 1 and `set -e` exits before
Quickshell launches. The helper now explicitly returns success. A regression test
covers empty, partial and populated optional environment configuration.

The repository now manages 32 runtime overlays (29 QML files and three scripts).
The user launcher is rendered from the same source as the runtime launcher, so
restores cannot silently lose this fix or deploy two different launcher versions.
The installer still owns version metadata and the migration ledger.

## Verification

- All managed configuration syntax, 29 QML overlays and 10 GLSL shaders checked.
- Temporary-home chezmoi apply/verify passed, including executable launcher parity.
- All 15 offline behavior tests passed.
- Upstream local-distribution tests passed, including its ten payload tests.
- The live systemd service started successfully after the launcher fix.
- Doctor passed the dependency, font, runtime, ABI, service, theme, environment
  and compositor configuration checks.
- Full-screen views of the desktop, sidebars, pill system monitor, equalizer and
  Settings were opened and inspected after the upgrade.
- GitHub CI is enabled for main pushes, pull requests and manual runs. The
  [initial hosted run](https://github.com/hrithikramprasath/dotfiles/actions/runs/35495436600)
  passed; subsequent results are shown in the README badge.

A broader qmlformat sweep passed 1,262 of 1,265 source files. Three unchanged
upstream files also fail when checked directly at the upstream revision:
`PillNotifs.qml`, `ClassicToggleDelegateChooser.qml` and
`LauncherSearchResult.qml`. This is a formatter limitation or upstream issue,
not a claim that every upstream file passes parsing. Those files are not custom
overlays; the running shell and inspected views loaded successfully.

There are non-fatal runtime warnings about inactive Hyprland/BlueZ integrations,
a stale notification image handle and NVIDIA VDPAU probing. Account-backed
services, all hardware features and every UI interaction were not retested.

## Remaining system migration

The updater could not authenticate sudo for migration 039, which removes an old
empty `InputMethod=` override from `/etc/sddm.conf.d/99-inir-theme.conf` and leaves
SDDM's backend policy to the installed distribution/provider. The existing file
already has no forced `DisplayServer=x11`. The user shell is running; the login
screen migration and privileged theme refresh remain pending.

Run `inir migrate` from an interactive terminal, review the migration and supply
your sudo password there. The updater also printed this theme-refresh command:

```bash
sudo bash ~/inir/scripts/sddm/install-pixel-sddm.sh
```

No SDDM restart was performed during the desktop session.

## Recovery and future updates

Before deployment, the old runtime, preferences, Niri config, launcher and user
service were backed up outside this public repository. The local checkout has a
`codex/pre-upgrade-2.31-20260920` branch pointing at the previous working revision.
The upgrade merge is `94ae2096`; the launcher fix is `c316f73c` in that checkout.
Neither local commit was pushed to the upstream iNiR project.

For rollback, restore the matching runtime, launcher and preferences together;
changing only `inir-revision.txt` does not roll back an installed shell. Review
`./setup rollback` before using it, and preserve any preferences changed since
the backup. Future upstream updates require merging and retesting these overlays.

## Screenshot scope

The new gallery contains actual 1600 × 900 PNG captures, not generated mockups.
An empty workspace was used, the right sidebar was temporarily switched to its
compact controls view, weather location was hidden and the idle visualizer was
hidden. Notifications and clipboard content were not cleared. The saved personal
configuration and original workspace were restored after capture. Existing
settings close-ups and vector illustrations remain alongside the new gallery.
