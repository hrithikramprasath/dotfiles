<p align="center">
  <img src="assets/overview.svg" alt="Dotfiles: an Arch Linux desktop built with Niri, iNiR and chezmoi" width="100%">
</p>

# Arch / Niri dotfiles

A personal Wayland desktop with scrolling workspaces, floating controls, and
wallpaper-derived colors across the shell, terminal and GTK/Qt apps. Managed with
[chezmoi](https://www.chezmoi.io/), built around [Niri](https://github.com/niri-wm/niri)
and [iNiR](https://github.com/snowarch/inir).

**[Install](docs/installation.md) · [Maintain](docs/maintenance.md) ·
[Review & compatibility](docs/review-2026-09-20.md) · [Attribution](THIRD_PARTY.md)**

This is a personal restore recipe for an existing Arch Linux installation.
Review the package lists and preferences before applying it to another machine.
The repository contains selected iNiR source overlays, not a complete shell.

## A closer look

| Wallpaper-derived palettes | Glass and rendering controls |
| --- | --- |
| ![iNiR Themes settings with the current palette and selectable color themes](assets/screenshots/themes.png) | ![iNiR Effects settings showing the blur backend and compositor blur control](assets/screenshots/effects.png) |

Captured from the running configuration on **20 September 2026**. These are
focused panel captures; account headers, app windows and desktop activity are
outside the capture area. The opening vector is an illustration, not a screenshot.

## The stack

| Layer | Configuration |
| --- | --- |
| Desktop | Niri + Quickshell / iNiR; modular compositor rules and custom QML overlays |
| Terminal | Kitty, Fish and Starship; shared Bash/Zsh login environment |
| Appearance | Wallpaper-driven Material You palette; GTK, Qt, Darkly and Kvantum |
| Utilities | Clipboard history, screenshots/OCR, mpv, Cava and EasyEffects |
| Restore | chezmoi templates, checksummed font downloads and pinned iNiR bootstrap |

## Get started

```bash
git clone https://github.com/hrithikramprasath/dotfiles.git ~/dotfiles
cd ~/dotfiles
# Review packages-repo.txt, packages-aur.txt and the configuration first.
./install.sh --full
```

`--full` can install system packages through sudo. Its manifests include kernels,
CPU microcode, a display manager and other machine-level choices; it is not a
minimal desktop-only installer. Personal applications are listed separately in
[`packages-apps.txt`](packages-apps.txt) and are not installed by the restore hook.

Already have iNiR installed? Start with `./install.sh --diff`, then use
`./install.sh --configs-only` when the changes are right. See the
[installation guide](docs/installation.md) for prerequisites and exact behavior.

![The four stages of restoration: review, install, apply and verify](assets/restore-flow.svg)

## Everyday controls

`Super` is the configured Niri modifier.

| Shortcut | Action |
| --- | --- |
| `Super + Enter` | Terminal |
| `Super + Space` | iNiR overview / launcher |
| `Super + V` | Clipboard history |
| `Super + ,` | Settings |
| `Super + Shift + S` | Screenshot / region menu |
| `Super + /` | Full shortcut reference |
| `Alt + Tab` | Niri's recent-window switcher |

The complete bindings live in
[`70-binds.kdl`](dot_config/niri/config.d/70-binds.kdl).

## What lives where

| Path | Purpose |
| --- | --- |
| `dot_config/` | Managed application configuration under `~/.config` |
| `dot_config/quickshell/inir/` | 31 selected runtime overlays: 29 QML files and two scripts |
| `dot_profile`, `dot_bash*`, `dot_z*` | Login environment and interactive shell setup |
| `.chezmoiscripts/` | Package synchronization and missing-runtime bootstrap |
| `.chezmoiexternal.toml` | Pinned font downloads and their licenses |
| `inir-revision.txt` | Tested base for fresh iNiR installs |
| `scripts/`, `tests/`, `.github/` | Offline validation and automation; never deployed into the home directory |
| `docs/`, `assets/` | Guides, review notes and documentation images |

## Validation and compatibility

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The validator checks configuration syntax, shader/QML parsing, local documentation
links and a restore into a temporary home. The behavior suite has **14 tests**.
Dependencies and runtime checks are in the [maintenance guide](docs/maintenance.md).
An [optional CI template](docs/examples/validate.yml) runs these checks on pushes
and pull requests without running the install hook.

The tested base remains **iNiR 2.30.0 / `dcba34ee`** with local overlays. Upstream
2.31.0 was reviewed; its larger Settings and panel changes need a separate overlay
migration. The current setup passes the documented checks, but hardware-specific
features and every possible desktop interaction have not been verified.

## Credits and license

Original repository work uses [MIT](LICENSE). iNiR-derived source retains
[GPL-3.0](LICENSES/GPL-3.0.txt); other assets retain their own terms. See
[third-party attribution](THIRD_PARTY.md) for scope and provenance.
