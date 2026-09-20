#!/usr/bin/env bash
# Dotfiles synchronization & full system restoration script powered by Chezmoi
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"

usage() {
    echo "Usage: ./install.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --configs-only    (Default) Apply managed dotfiles without running package scripts"
    echo "  --full            Apply configs and install/sync repository and AUR packages via Chezmoi"
    echo "  --diff            Preview differences between your repository and active files"
    echo "  --verify          Verify that local configs match the repository (checks for drift)"
    echo "  -h, --help        Show this help message"
}

ensure_chezmoi() {
    if ! command -v chezmoi >/dev/null 2>&1; then
        echo "Installing chezmoi from Arch's official repository..."
        sudo pacman -Syu --needed --noconfirm chezmoi
    fi

    # Ensure source directory is linked and configured
    mkdir -p "$HOME/.config/chezmoi" "$HOME/.local/share"
    if [ ! -e "$HOME/.local/share/chezmoi" ]; then
        ln -sfn "$DOTFILES_DIR" "$HOME/.local/share/chezmoi"
    fi

    if [ ! -f "$HOME/.config/chezmoi/chezmoi.toml" ]; then
        local source_literal
        source_literal=$(chezmoi execute-template -S "$DOTFILES_DIR" '{{ .chezmoi.sourceDir | toJson }}')
        cat << EOF > "$HOME/.config/chezmoi/chezmoi.toml"
sourceDir = $source_literal

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
    if [ $# -ne 1 ]; then
        usage >&2
        exit 1
    fi
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

if [[ "$MODE" == full ]]; then
    if [[ "$EUID" == 0 ]]; then
        echo "Run ./install.sh --full as your normal login user, not root or sudo." >&2
        exit 1
    fi
    if ! command -v pacman >/dev/null || ! command -v sudo >/dev/null; then
        echo "A booted Arch installation with sudo access is required." >&2
        exit 1
    fi
    if [[ ! -d /run/systemd/system ]]; then
        echo "Boot the installed Arch system first; do not run this in arch-chroot or the live ISO." >&2
        exit 1
    fi
    for var in XDG_CONFIG_HOME XDG_DATA_HOME XDG_STATE_HOME; do
        case "$var" in
            XDG_CONFIG_HOME) expected="$HOME/.config" ;;
            XDG_DATA_HOME) expected="$HOME/.local/share" ;;
            XDG_STATE_HOME) expected="$HOME/.local/state" ;;
        esac
        if [[ -n "${!var:-}" && "${!var}" != "$expected" ]]; then
            echo "This restore expects $var=$expected; unset your custom override first." >&2
            exit 1
        fi
    done
    sudo -v
    systemctl --user show-environment >/dev/null || {
        echo "No systemd user session. Log into a TTY as your normal user (not through su) and retry." >&2
        exit 1
    }
fi

# Inspection must not bootstrap tools, create config files, or link directories.
if [[ "$MODE" == diff || "$MODE" == verify ]]; then
    if ! command -v chezmoi >/dev/null 2>&1; then
        echo "chezmoi is required for --$MODE; install it first." >&2
        exit 1
    fi
else
    ensure_chezmoi
fi

case "$MODE" in
    configs)
        if [[ ! -f "$HOME/.config/quickshell/inir/shell.qml" ]]; then
            echo "iNiR is not installed. Run ./install.sh --full first." >&2
            exit 1
        fi
        echo "Applying dotfiles via Chezmoi (excluding package scripts)..."
        chezmoi apply -S "$DOTFILES_DIR" -x scripts
        echo "Configuration files applied successfully!"
        ;;
    full)
        echo "Running full system synchronization via Chezmoi..."
        chezmoi apply -S "$DOTFILES_DIR"
        echo "Desktop installation completed. Reboot, then select Niri in SDDM."
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
echo "Done."
