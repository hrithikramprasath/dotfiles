# Desktop verification and cleanup — 2026-09-19

## Completed work

Continued the interrupted setup audit, preserved existing changes, and checked
both the restore recipe and running Arch/Niri/iNiR desktop at 1600×900.

The first live sweep captured 77 views: the desktop, 21 sidebar destinations,
28 settings pages, shared dialogs and overlays, and 11 pill surfaces. All were
visually inspected. Seven slow-loading views were recaptured after four seconds;
the initially blank settings, shortcuts and wallpaper previews rendered normally.
The Autostart page was captured again after its fix. Capture success alone is not
a functional test of every control, service or hardware integration.

The inactive Waffle desktop family was not enabled. The legacy iNiR AltSwitcher
IPC call produced no visible switcher; the current config binds Alt+Tab through
Niri's native recent-windows block. That native keyboard interaction was not
visually verified. The laptop battery path could only be checked in its absent
battery state on this desktop. Power/logout actions were not executed.

## Additional defects fixed

- Autostart settings used `onCheckedChanged`, which writes during initial binding
  evaluation. Combined with a stale file model, merely opening settings restored
  a removed duplicate Discord startup command. Switches now write only on user
  toggles, and the file model reparses on every successful FileView load.
- The live regression restarted iNiR, removed the duplicate externally, verified
  the in-memory entry count fell from three to two, then opened and closed the
  settings page and checked that the startup file stayed byte-identical.
- Chezmoi now preserves mode 0700 for `~/.local` and 0600 for the EasyEffects
  equalizer config. An isolated restore test verifies both modes.
- The calculator and wallpaper fixes now match across the live runtime, local
  iNiR development checkout and dotfiles overlay. All 31 overlay files match.

## Validation

- 13 offline dotfiles regression tests passed.
- All 29 QML overlay files parse with Qt tooling.
- Isolated Chezmoi apply/verify and rendered Niri configuration validation passed.
- An earlier iNiR doctor run passed all 27 checks. The final run passed 26
  and flagged the customized checkout as diverged from `origin/main` (five local
  commits and 159 upstream commits before this audit commit). Runtime checks
  passed; no automatic repair or upstream merge was performed.
- iNiR local-distribution suite passed, including 10 runtime-payload tests.
- No failed system/user units at inspection; no QML ReferenceError, TypeError,
  assignment errors or binding loops appeared in the reviewed capture logs.
- Bluetooth discovery and an SVG pattern emitted warnings; these were not
  silently counted as QML correctness failures or suppressed.

## Cleanup and retained applications

The earlier pass recorded about 2.06 GiB of obsolete build archives, thumbnails,
package-download caches and an old Cursor runtime removed. This continuation
removed 577,495,495 bytes (about 551 MiB) of npm cache data. Filesystem compression
means logical file bytes need not equal physical free-space gains. Temporary QA
screenshots are deleted after inspection; private screenshots and conversation
history are not committed.

Alacritty is already uninstalled. Pacman reports no orphaned packages, and
`paccache -d -k 2` found nothing eligible for removal. Pavucontrol, Blueman,
NetworkManager's editor, Fuzzel, Swayidle, Swaylock, Mission Center and the wallpaper
backend are used by iNiR or declared dependencies. The wlr portal is a dependency
of the installed Niri package. Removing them just because the shell has similar
controls would break settings, fallbacks or package dependencies. Browser data,
Steam games/Proton installations and active tool runtimes were retained.

## External limitations

Wallhaven reported an upstream error and displayed its fallback-provider controls.
AI features require a configured provider or local model. No credentials were
added to the repository.

The pre-existing experimental `~/inir/scripts/e2e_test_runner.py` and its `tests/`
scaffold are preserved untracked. Some of its checks only assert a screenshot
exists and its clipboard test overwrites clipboard contents; its sweeping pass
claims were not used as evidence for this report.

## Implementation references

- [Qt AbstractButton toggled signal](https://doc.qt.io/qt-6/qml-qtquick-controls-abstractbutton.html#toggled-signal) fires on interactive changes.
- [Quickshell FileView](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/FileView/) provides a successful-load signal for reload completion.

## Repository refresh

See the [20 September review](review-2026-09-20.md) for the public documentation
refresh, updated application flags, provenance notes and reproducible validator.
