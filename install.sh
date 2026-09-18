#!/usr/bin/env bash
# Dotfiles synchronization & full system restoration script
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SOURCE="$DOTFILES_DIR/.config"
CONFIG_TARGET="${XDG_CONFIG_HOME:-$HOME/.config}"

usage() {
    echo "Usage: ./install.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --configs-only    (Default) Link configuration files to ~/.config"
    echo "  --full            Install official packages, AUR packages, setup iNiR, and link configs"
    echo "  -h, --help        Show this help message"
}

install_packages() {
    echo "=== 1/4: Installing official repository packages ==="
    if [ -f "$DOTFILES_DIR/packages-repo.txt" ]; then
        sudo pacman -S --needed --noconfirm - < "$DOTFILES_DIR/packages-repo.txt"
    else
        echo "Warning: packages-repo.txt not found, skipping official packages."
    fi

    echo "=== 2/4: Checking AUR helper (yay) ==="
    if ! command -v yay >/dev/null 2>&1; then
        echo "Installing yay..."
        tmp_dir=$(mktemp -d)
        git clone https://aur.archlinux.org/yay.git "$tmp_dir/yay"
        (cd "$tmp_dir/yay" && makepkg -si --noconfirm)
        rm -rf "$tmp_dir"
    fi

    echo "=== 3/4: Installing AUR packages ==="
    if [ -f "$DOTFILES_DIR/packages-aur.txt" ]; then
        yay -S --needed --noconfirm - < "$DOTFILES_DIR/packages-aur.txt"
    else
        echo "Warning: packages-aur.txt not found, skipping AUR packages."
    fi

    echo "=== 4/4: Setting up iNiR shell repository ==="
    if [ ! -d "$HOME/inir" ]; then
        echo "Cloning iNiR repository..."
        git clone https://github.com/snowarch/inir.git "$HOME/inir"
        if [ -f "$HOME/inir/setup" ]; then
            bash "$HOME/inir/setup" install --non-interactive || true
        elif [ -f "$HOME/inir/setup.sh" ]; then
            bash "$HOME/inir/setup.sh" install --non-interactive || true
        fi
    fi
}

link_configs() {
    echo "Deploying dotfiles from $CONFIG_SOURCE to $CONFIG_TARGET..."
    mkdir -p "$CONFIG_TARGET"

    for item in "$CONFIG_SOURCE"/*; do
        [ -e "$item" ] || continue
        name="$(basename "$item")"
        target="$CONFIG_TARGET/$name"

        if [ -L "$target" ]; then
            rm -f "$target"
        elif [ -e "$target" ]; then
            backup="${target}.backup.$(date +%Y%m%d_%H%M%S)"
            echo "Backing up existing $name -> $backup"
            mv "$target" "$backup"
        fi

        echo "Linking $name -> $target"
        ln -s "$item" "$target"
    done
    echo "Configuration files linked successfully!"
}

MODE="configs"
if [ $# -gt 0 ]; then
    case "$1" in
        --full)
            MODE="full"
            ;;
        --configs-only)
            MODE="configs"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
fi

if [ "$MODE" = "full" ]; then
    install_packages
fi

link_configs

echo ""
echo "All done! Your Niri + iNiR environment is ready."
