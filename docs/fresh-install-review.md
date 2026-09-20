# Fresh-install review — 20 September 2026

The original restore was incomplete for a bare Arch TTY installation. The corrected
`--full` path is intended to install the desktop and login UI without selecting
personal applications. [Installation instructions](installation.md) define the
base-system prerequisites and the first-login checks.

## Gaps corrected

| Gap | Change |
| --- | --- |
| Package list mixed desktop dependencies with kernels, microcode, boot/filesystem and snapshot choices | Removed those choices from the desktop manifest |
| Missing explicit backend for SDDM's default X11 greeter | Added `xorg-server` and `xorg-xauth`; Niri remains a Wayland session |
| Package installation could rely on stale repository databases | Use `pacman -Syu --needed`; bootstrap chezmoi from Arch |
| Upstream installer could run a second independent dependency plan | Use the pinned installer's `--skip-deps` path |
| Successful unchanged chezmoi hook could be skipped on retry | Before/after hooks run on every full apply |
| Upstream default wallpaper palette generated before personal configs arrived | Deploy a reviewed palette seed and Qt colors with the intended wallpaper |
| GTK4/dconf state and service enablement were not enforced after restore | Add a final setup stage with Niri/Python/file checks, dconf settings and service wiring |
| Login theme failure could be treated as an optional warning | Require SDDM installation/synchronization and verify its theme, background and enablement |
| Root/chroot/custom-XDG invocation could write to the wrong environment | Reject unsupported full-install contexts before mutation |
| Existing unrelated or incompatible iNiR could receive full-file overlays | Verify checkout ancestry and installed runtime version before applying |
| Discord autostart and ProtonPlus timers were personal application integration | Remove them from deployment |
| Floating-image preference referenced an absent personal picture; quick-launch referenced uninstalled Code | Clear the image selection and remove the Code shortcut |

The package lists still include desktop utilities: Kitty, Nautilus, EasyEffects,
media tools, screenshot/OCR tools, fonts, themes and hardware-control helpers.
`packages-apps.txt` is not consumed by either hook. Only explicitly reviewed color
files are stored under the state directory; accounts, history and credentials are
not part of this restore.

## Evidence and limits

- Official desktop packages resolved successfully against the local Arch sync
  databases; all 11 named AUR packages were found through the AUR RPC API.
- Offline validator passed: syntax, QML/GLSL, documentation links, an isolated
  chezmoi apply/verify, Niri includes, private modes and deployment exclusions.
- A new Python 3.12 virtual environment installed the pinned upstream
  requirements successfully; color, image, GTK and media helper imports passed.
- 22 regression tests passed. New tests exercise finalizer success/failure
  ordering, missing wallpaper, theme failure, manifest separation, incompatible
  runtime rejection and preservation of unrelated checkouts. Package managers,
  services and privileged writes are stubbed; system fixture paths are redirected
  to a temporary directory.
- The preceding iNiR 2.31 upgrade and six-image README gallery passed hosted CI
  at commit `9eaff62`. Subsequent runs are visible on the README badge.

No disks were erased, no live display manager was restarted, and no fresh-disk VM
boot was performed for this review. A package resolution check does not prove
that every future AUR build or mirror download will succeed. First boot, GPU
support, user authentication and hardware-specific controls still require testing
on the new installation. The installer stops on detected failures instead of
claiming completion.

The earlier live machine's privileged SDDM migration still needs authentication;
this review did not run the full installer on the existing desktop. A future full
install's final stage applies the corrected SDDM theme configuration.

References: [SDDM setup](https://wiki.archlinux.org/title/SDDM),
[Arch partial upgrades](https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported),
[Niri sessions](https://github.com/niri-wm/niri/wiki/Getting-Started).
