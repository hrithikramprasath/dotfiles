# Installation

This repository restores a personal user environment on **Arch Linux**. It does
not partition disks, install a bootloader or guarantee the same result on another
machine. Start from a working user account, network connection and Arch install.

## Before applying

1. Back up existing dotfiles or inspect the changes with chezmoi before applying.
2. Review `packages-repo.txt` and `packages-aur.txt`. The official list includes
   `linux`, `linux-lts`, both CPU microcode packages, SDDM, networking and other
   machine-level choices. Keep only the choices appropriate for your machine.
3. Review Niri input/output preferences, startup apps and shell preferences.
   Discord is an optional app but appears in this personal startup configuration.
4. Run installation as your normal user with sudo access, not as root. AUR
   packages are built as that user. Git, curl and a functioning pacman are needed;
   the official package step includes build tools for the AUR helper.

## Clone, inspect, install

```bash
git clone https://github.com/hrithikramprasath/dotfiles.git ~/dotfiles
cd ~/dotfiles
# If chezmoi is already installed:
./install.sh --diff
# After reviewing the recipe:
./install.sh --full
```

The wrapper bootstraps chezmoi into `~/.local/bin` if needed, then applies the
source. It does not overwrite an existing chezmoi configuration file. Every
wrapper command explicitly uses this checkout as its source; if plain `chezmoi`
points elsewhere, pass `--source ~/dotfiles` or update your local chezmoi config.

The package hook installs required official/AUR packages, clones a missing
`~/inir` at the revision in `inir-revision.txt`, and runs its installer when the
runtime, launcher or Python environment is missing. An existing iNiR checkout is
preserved. Installation failures stop the restore rather than being hidden.

Font downloads come from pinned Google Fonts commits and have SHA-256 checksums.
A network connection is needed for those assets even in configs-only mode when
not already cached.

## Wrapper options

| Command | Behavior |
| --- | --- |
| `./install.sh --diff` | Preview differences; requires chezmoi and creates no bootstrap files |
| `./install.sh --verify` | Check managed-file drift; exits nonzero when files differ |
| `./install.sh --configs-only` | Apply home/config files, excluding install scripts; requires an existing iNiR runtime |
| `./install.sh --full` | Apply files and run changed package hooks |

No option is equivalent to a distribution upgrade. Chezmoi's `run_onchange`
hook runs only when its rendered contents change; `--full` does not force a
successful, unchanged hook to rerun. To repair a missing runtime with an unchanged
hook, review and run the installer in your existing `~/inir` checkout, then apply
the dotfiles again. Do not reset a customized checkout to upstream to repair it.

## Optional applications

`packages-apps.txt` is a separate convenience list. Review it before installing:

```bash
yay -S --needed - < packages-apps.txt
```

Optional utilities can still be required for particular shell features. For
example, removing an audio/network editor because a shell panel looks similar
can remove its fallback settings interface.

The ProtonPlus user service and timer are provided but not enabled automatically.
If you use ProtonPlus and want hourly updates, inspect the unit, then run:

```bash
systemctl --user daemon-reload
systemctl --user enable --now protonplus.timer
```

## After installation

```bash
./install.sh --verify
niri validate -c ~/.config/niri/config.kdl
inir doctor
systemctl --user status inir.service
```

Use the installed Niri session from your login manager, or an appropriately
configured `niri-session`. Log out and back in when applying environment changes;
reopening a terminal does not change the compositor's environment. Browser flags
take effect when the corresponding application is fully restarted.

Do not run both a compositor autostart entry and `inir.service` for the shell.
The managed configuration expects the systemd service to own iNiR.

Read [maintenance](maintenance.md) before editing or updating the runtime.
