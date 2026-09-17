#!/usr/bin/env bash
# Dotfiles synchronization / installation script
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SOURCE="$DOTFILES_DIR/.config"
CONFIG_TARGET="${XDG_CONFIG_HOME:-$HOME/.config}"

echo "Deploying dotfiles from $DOTFILES_DIR to $CONFIG_TARGET..."

mkdir -p "$CONFIG_TARGET"

for item in "$CONFIG_SOURCE"/*; do
    name="$(basename "$item")"
    target="$CONFIG_TARGET/$name"

    if [ -e "$target" ] || [ -L "$target" ]; then
        echo "Backing up existing $name to ${target}.backup"
        mv "$target" "${target}.backup"
    fi

    echo "Linking $name -> $target"
    ln -s "$item" "$target"
done

echo "Dotfiles installation complete!"
