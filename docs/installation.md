# Install the desktop on fresh Arch

`./install.sh --full` is a **desktop installer for a booted Arch Linux system**.
It installs Niri/iNiR, the SDDM login theme, desktop tools, fonts, icons, audio,
portals and the tracked appearance/configuration. It does not install your
personal application list or restore personal documents, accounts or history.

## Starting point

Finish the Arch installation first: disks, bootloader, kernel/firmware, appropriate
GPU drivers, network access and a normal user with a password and sudo access.
Reboot into that installed system and log into a TTY as that user. Do not run the
desktop installer as root, through `su`, inside `arch-chroot`, or from the live ISO.

Git must be installed before the clone command. If needed, as your normal user:

```bash
sudo pacman -Syu --needed git
```

If sudo or your user account is not configured yet, finish that part of the Arch
installation first. Use a working network connection throughout the install.

## Install

```bash
git clone https://github.com/hrithikramprasath/dotfiles.git ~/dotfiles
cd ~/dotfiles
# Review the desktop package lists and configuration.
./install.sh --full
```

Supply your sudo password when requested. AUR builds run as your normal user.
The package step performs a full pacman upgrade to avoid an unsupported partial
upgrade; it can therefore update applications you already installed, but it does
not select anything from `packages-apps.txt`. On a fresh install that list is never
installed. Network or AUR failures stop the command: fix the reported cause and
rerun the same command. Both setup hooks run again on each full apply.

After a successful completion:

```bash
reboot
```

Choose **Niri** in SDDM's session selector and log in. The installer enables SDDM
for the next boot without restarting the login manager during installation. Kitty
uses Fish; the account's login shell does not need to be changed.

## What the full command does

1. Checks for a normal user, a booted systemd system, a usable user session and
   sudo access. This recipe expects the standard `~/.config` and `~/.local` paths.
2. Installs chezmoi from Arch if missing; installs the desktop manifests with
   pacman and yay, including build tools and the Xorg backend used by SDDM's
   default greeter. The desktop session itself is Wayland.
3. Clones a missing `~/inir` at the tested revision and runs its file/service
   installer with `--skip-deps`, so this repository owns the package selection.
   Installs the shell's Python environment. Existing customized checkouts are
   preserved; incompatible checkout/runtime versions stop deployment.
4. Applies the personal desktop layout, patched launcher/QML, wallpaper, GTK/Qt
   configuration, fonts and a curated color palette. Only appearance data is
   seeded under `.local/state`; no session histories or credentials are restored.
5. Checks the runtime, Python imports, wallpaper, launcher parity and Niri syntax.
   Applies GTK settings through dconf, installs/syncs the ii-pixel SDDM theme
   **after** the restored wallpaper and palette are in place, and requires success.
6. Enables NetworkManager, Bluetooth, power profiles, SDDM, PipeWire/WirePlumber
   and the iNiR service linked specifically to `niri.service`. Selects the graphical
   boot target. The wrapper prints completion only if the final checks pass.

The wallpaper is an intentional desktop appearance asset. The repository does
not include your home-directory contents, browser profiles, passwords, private
files or account avatar. Usernames/avatars, detected devices, screen dimensions,
network/weather/media data and notification contents naturally differ on a new
installation. The screenshot gallery includes a staged compact-sidebar view;
see its capture notes for the temporary presentation settings.

## Desktop packages versus personal applications

`packages-repo.txt` and `packages-aur.txt` contain the desktop and its supporting
tools: terminal, file manager, audio controls, screenshots/OCR and shell features.
They do not choose kernels, CPU microcode, a bootloader, filesystem tools, a
snapshot policy or a firewall. Those belong to the base Arch installation.

`packages-apps.txt` is a reference list only. Install whichever personal apps you
want afterward; no installer hook reads that file. Discord is no longer a default
autostart entry, and ProtonPlus timer units are no longer deployed. Optional app
appearance templates/flags are still configuration; they do not install the apps.

## Existing machines and wrapper options

Back up existing configuration before applying. Every wrapper command uses this
checkout as its source without replacing an existing chezmoi source setting.
The two full-mode hooks may also run with plain `chezmoi apply`; use the wrapper's
configs-only option for a configuration-only update.

| Command | Behavior |
| --- | --- |
| `./install.sh --diff` | Read-only preview; requires chezmoi |
| `./install.sh --verify` | Check managed-file drift; nonzero if different |
| `./install.sh --configs-only` | Apply home files without either setup hook; requires an existing compatible runtime |
| `./install.sh --full` | Install/update desktop dependencies, apply files and configure login/services |

`--full` is intended to select this desktop, including SDDM. Review it carefully
on a machine with another login manager or network/audio stack. It does not
silently reset a customized iNiR checkout to upstream. Follow the
[maintenance guide](maintenance.md) to migrate an incompatible installed version.
A changed pin alone does not upgrade an existing runtime.

## Verify after the first graphical login

```bash
niri validate -c ~/.config/niri/config.kdl
inir doctor
systemctl --user status inir.service
systemctl status sddm.service
./install.sh --verify
```

Settings and wallpaper generation can legitimately change managed files after
login; inspect drift with `--diff`. Never start a second shell from a compositor
autostart entry: `inir.service` owns it.

The automated checks exercise a temporary-home restore, mocked installer/service
failure paths, current package resolution and configuration syntax. They are not
a fresh-disk VM boot test or a guarantee across GPUs, mirrors and future rolling
releases. See the [fresh-install review](fresh-install-review.md) for evidence.

References: [Arch system maintenance](https://wiki.archlinux.org/title/System_maintenance),
[SDDM](https://wiki.archlinux.org/title/SDDM), and
[Niri session setup](https://github.com/niri-wm/niri/wiki/Getting-Started).
