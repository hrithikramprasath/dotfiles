#!/usr/bin/env bash

# This script provides path resolution helpers for quickshell/inir
# It is sourced by the main executable_inir launcher as well as auxiliary scripts

# Resolves the path to the user's pictures directory, primarily using xdg-user-dir
get_pictures_dir() {
    if command -v xdg-user-dir &> /dev/null; then
        xdg-user-dir PICTURES
        return
    fi

    local config_file="${XDG_CONFIG_HOME:-$HOME/.config}/user-dirs.dirs"
    if [ -f "$config_file" ]; then
        local pictures_path
        pictures_path=$(source "$config_file" >/dev/null 2>&1; echo "$XDG_PICTURES_DIR")
        echo "${pictures_path/#\$HOME/$HOME}"
        return
    fi

    echo "$HOME/Pictures"
}
