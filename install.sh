#!/usr/bin/env bash
# Dotfiles synchronization & full system restoration script powered by Chezmoi
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Usage: ./install.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --configs-only    (Default) Apply configuration files to ~/.config without running package scripts"
    echo "  --full            Apply configs and install/sync repository and AUR packages via Chezmoi"
    echo "  --diff            Preview differences between your repository and active files"
    echo "  --verify          Verify that local configs match the repository (checks for drift)"
    echo "  -h, --help        Show this help message"
}

ensure_chezmoi() {
    if ! command -v chezmoi >/dev/null 2>&1; then
        echo "Installing chezmoi into ~/.local/bin..."
        mkdir -p "$HOME/.local/bin"
        sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$HOME/.local/bin"
        export PATH="$HOME/.local/bin:$PATH"
    fi

    # Ensure source directory is linked and configured
    mkdir -p "$HOME/.config/chezmoi" "$HOME/.local/share"
    if [ ! -e "$HOME/.local/share/chezmoi" ]; then
        ln -sfn "$DOTFILES_DIR" "$HOME/.local/share/chezmoi"
    fi

    if [ ! -f "$HOME/.config/chezmoi/chezmoi.toml" ]; then
        cat << EOF > "$HOME/.config/chezmoi/chezmoi.toml"
sourceDir = "$DOTFILES_DIR"

[edit]
    apply = true

[diff]
    pager = "cat"

[git]
    autoCommit = false
    autoPush = false
EOF
    fi
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
        --diff)
            MODE="diff"
            ;;
        --verify)
            MODE="verify"
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

ensure_chezmoi

case "$MODE" in
    configs)
        echo "Applying dotfiles via Chezmoi (excluding package scripts)..."
        chezmoi apply -S "$DOTFILES_DIR" -x scripts
        echo "Configuration files applied successfully!"
        ;;
    full)
        echo "Running full system synchronization via Chezmoi..."
        chezmoi apply -S "$DOTFILES_DIR"
        echo "Full system sync completed successfully!"
        ;;
    diff)
        echo "Showing differences between repository and active configs:"
        chezmoi diff -S "$DOTFILES_DIR"
        ;;
    verify)
        echo "Verifying local configurations against repository..."
        if chezmoi verify -S "$DOTFILES_DIR" -x scripts; then
            echo "Everything matches! Zero configuration drift."
        else
            echo "Drift detected. Run './install.sh --diff' to view differences."
            exit 1
        fi
        ;;
esac

echo ""
echo "Done! Your environment is synchronized."
