# Maintenance

## Source and runtime ownership

There are three related locations:

- This chezmoi source stores selected configuration and iNiR overlays.
- `~/inir` is the upstream development/installer checkout, including local commits.
- `~/.config/quickshell/inir` is the installed runtime that the shell actually uses.

The pinned bootstrap revision is not a version lock on an already-installed
runtime. Updating `inir-revision.txt` alone neither upgrades an existing checkout
nor makes old full-file QML overlays compatible with a new release.

The installer owns `.config/inir/version`, `version.json` and `migrations.json`.
They are excluded from deployment and are no longer tracked as stale snapshots.
Keep the exclusion even after removing their source files: it prevents accidentally
adding local runtime state back into the restore recipe.

## Edit, review, apply

```bash
chezmoi diff --source ~/dotfiles
chezmoi edit --source ~/dotfiles ~/.config/niri/config.kdl
chezmoi apply --source ~/dotfiles --exclude scripts
chezmoi verify --source ~/dotfiles --exclude scripts
```

This repository enables `edit.apply`, so `chezmoi edit` applies the edit when the
editor closes. For staged review instead, edit source files directly. Template
filenames differ from deployed filenames: `40-environment.kdl.tmpl` becomes
`40-environment.kdl`.

Wallpaper generation and the Settings UI write several managed files. That can
produce normal drift. Inspect the diff before either overwriting live preferences
or importing them. `chezmoi add` is not a privacy filter.

## Updating iNiR

Read the upstream changelog and compare changes to the 32 overlaid files before
installing a new runtime. Back up the current checkout, runtime and preferences.
Port the overlays on a separate branch, check dynamic QML bindings in a session,
and update the pin only after verifying the resulting combination. A clean
parser result alone is not enough to prove runtime compatibility.

The tested baseline is now 2.31.0 (`9574fa42`) with migrated custom overlays.
The launcher is managed in both the runtime and `~/.local/bin` from one source
file; preserve its optional-environment startup fix during future merges.
See the [upgrade report](upgrade-2.31.md) for checks and recovery details.
Doctor reporting local commits ahead of upstream is expected for this branch.

Niri already starts modern xwayland-satellite on demand. Do not add a second
manual satellite startup process or force a fixed `DISPLAY` value.

## Local validation

Required tools on Arch: Python 3.11+, Bash, chezmoi, jq, Node.js, Fish, Niri,
`qt6-declarative` (qmlformat) and `glslang` (glslangValidator).

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

The validator runs without network access and never applies to the real home.
It renders into a temporary destination, excluding install scripts and external
font payloads. It checks Bash/Fish, JSON, TOML, XML/SVG, QML and GLSL syntax,
rendered Niri includes, private file modes, the Kitty theme link and repository-only
path exclusions. It does not execute Zsh or validate remote provider availability.

The [active GitHub Actions workflow](../.github/workflows/validate.yml) runs these
checks for pushes to `main`, pull requests and manual dispatch. It uses an Arch
container, read-only repository permissions and a commit-pinned checkout action.
Container preparation installs validation tools and requires network access;
the checks do not install your desktop. The first hosted run passed on
20 September 2026. The [example copy](examples/validate.yml) is retained for reuse.

After changes to live behavior, also check `inir doctor`, service logs and the
affected UI. Hardware, account-backed features and different display sizes need
separate checks. The earlier [live QA report](desktop-verification-2026-09-19.md)
describes the 77-view inspection and its limits.

## Publishing from a personal machine

Before pushing, review the staged diff and any images. Never add API keys, Wi-Fi
credentials, cookies, shell history, logs, private conversations or backup folders.
The `private_` chezmoi prefix changes permissions; it does **not** encrypt content
or hide it from a public Git repository. Likewise, `.gitignore` does not protect
files that are already tracked.

The tracked hotspot password is iNiR's public example default, not a secret.
Choose a private passphrase locally before using the hotspot, and exclude or
template it before importing Settings changes. Provider credentials should remain
in their local credential stores, outside this source tree.

Documentation captures should show a bounded settings panel or a sanitized demo
session. Inspect the actual pixels before staging: filenames alone say nothing
about notification, clipboard or account information inside a screenshot.
Replacing an image in a new commit does not erase older images from Git history.
