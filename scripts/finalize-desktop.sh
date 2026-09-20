#!/usr/bin/env bash
# Runs after chezmoi has applied the desktop files; no session restart.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
config_dir="${XDG_CONFIG_HOME:-$HOME/.config}"
runtime="$config_dir/quickshell/inir"

fail() { echo "Desktop setup incomplete: $*" >&2; exit 1; }
for file in "$runtime/shell.qml" "$config_dir/inir/config.json" \
    "$config_dir/systemd/user/inir.service" /usr/share/wayland-sessions/niri.desktop \
    "$HOME/.local/share/color-schemes/Darkly.colors" \
    "$HOME/.local/state/quickshell/user/generated/colors.json"; do
    [[ -s "$file" ]] || fail "missing $file"
done
for command in niri qs Xorg gsettings fc-cache; do
    command -v "$command" >/dev/null || fail "missing command $command"
done
[[ -x "$HOME/.local/state/quickshell/.venv/bin/python" ]] || fail "missing iNiR Python environment"
"$HOME/.local/state/quickshell/.venv/bin/python" -c 'import materialyoucolor, numpy, PIL'
cmp -s "$runtime/scripts/inir" "$HOME/.local/bin/inir" || fail "launcher copies differ"
jq -e 'type == "object"' "$config_dir/inir/config.json" >/dev/null
wallpaper=$(jq -er '.background.wallpaperPath' "$config_dir/inir/config.json")
[[ -s "$wallpaper" ]] || fail "missing configured wallpaper: $wallpaper"
niri validate -c "$config_dir/niri/config.kdl"

# GTK4 reads dconf through the portal; settings.ini alone is not sufficient.
# These match the managed GTK/KDE files. This works from a real TTY login too.
gsettings set org.gnome.desktop.interface color-scheme prefer-dark
gsettings set org.gnome.desktop.interface gtk-theme adw-gtk3-dark
gsettings set org.gnome.desktop.interface icon-theme WhiteSur-dark
gsettings set org.gnome.desktop.interface cursor-theme capitaine-cursors-light
gsettings set org.gnome.desktop.interface cursor-size 24
gsettings set org.gnome.desktop.interface font-name 'Roboto Flex 11'
fc-cache -f
xdg-user-dirs-update

# Theme installation must succeed, not merely print an upstream warning.
# Its synchronizer reads the restored palette and wallpaper after deployment.
sddm_installer="$HOME/inir/scripts/sddm/install-pixel-sddm.sh"
[[ -f "$sddm_installer" ]] || fail "missing pinned SDDM theme installer"
INIR_SDDM_AUTO_APPLY=yes bash "$sddm_installer"
[[ -s /usr/share/sddm/themes/ii-pixel/Main.qml ]] || fail "SDDM theme missing"
[[ -s /usr/share/sddm/themes/ii-pixel/assets/background.png ]] || fail "SDDM wallpaper missing"
grep -q '^Current=ii-pixel$' /etc/sddm.conf.d/99-inir-theme.conf || fail "SDDM theme not selected"

# Enable for the next boot. Do not start/restart a display manager, disconnect
# the installation network, or change audio devices in the current session.
sudo systemctl enable NetworkManager.service bluetooth.service power-profiles-daemon.service sddm.service
sudo systemctl set-default graphical.target
systemctl --user daemon-reload
inir service enable
systemctl --user enable pipewire.socket pipewire-pulse.socket wireplumber.service
[[ -L "$config_dir/systemd/user/niri.service.wants/inir.service" ]] || fail "shell autostart not wired"
systemctl is-enabled --quiet sddm.service || fail "SDDM not enabled"
echo "Desktop files, wallpaper, login theme and next-login services verified."
