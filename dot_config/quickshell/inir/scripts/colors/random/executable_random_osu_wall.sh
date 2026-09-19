#!/usr/bin/env bash

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

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
PICTURES_DIR=$(get_pictures_dir)
CACHE_DIR="$XDG_CACHE_HOME/quickshell"
STATE_DIR="$XDG_STATE_HOME/quickshell"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=scripts/lib/config-path.sh
source "$SCRIPT_DIR/../../lib/config-path.sh"

mkdir -p "$PICTURES_DIR/Wallpapers"

# 1. Try osu! seasonal backgrounds API
link=""
response=$(curl -fsSL --max-time 8 "https://osu.ppy.sh/api/v2/seasonal-backgrounds" 2>/dev/null || true)
if [ -n "$response" ] && echo "$response" | jq empty 2>/dev/null; then
    images=$(echo "$response" | jq '.backgrounds | length' 2>/dev/null || echo 0)
    if [ "$images" -gt 0 ]; then
        randomIndex=$((RANDOM % images))
        link=$(echo "$response" | jq -r ".backgrounds[$randomIndex].url // empty" 2>/dev/null || true)
    fi
fi

# 2. High-reliability fallback: Bing Daily 4K/UHD Wallpapers
if [ -z "$link" ] || [ "$link" = "null" ]; then
    bingResponse=$(curl -fsSL --max-time 10 "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=en-US" 2>/dev/null || true)
    if [ -n "$bingResponse" ] && echo "$bingResponse" | jq empty 2>/dev/null; then
        bingCount=$(echo "$bingResponse" | jq '.images | length' 2>/dev/null || echo 0)
        if [ "$bingCount" -gt 0 ]; then
            randomIndex=$((RANDOM % bingCount))
            relUrl=$(echo "$bingResponse" | jq -r ".images[$randomIndex].url // empty" 2>/dev/null || true)
            if [ -n "$relUrl" ]; then
                link="https://www.bing.com$relUrl"
            fi
        fi
    fi
fi

if [ -z "$link" ] || [ "$link" = "null" ]; then
    echo "Failed to retrieve wallpaper from provider or daily fallback." >&2
    exit 1
fi

ext=$(echo "$link" | awk -F. '{print $NF}' | cut -d'&' -f1 | cut -d'?' -f1)
[ -z "$ext" ] && ext="jpg"
downloadPath="$PICTURES_DIR/Wallpapers/random_wallpaper.$ext"
illogicalImpulseConfigPath="$(inir_config_file)"
currentWallpaperPath=$(jq -r '.background.wallpaperPath // empty' "$illogicalImpulseConfigPath" 2>/dev/null || true)
if [ "$downloadPath" == "$currentWallpaperPath" ]; then
    downloadPath="$PICTURES_DIR/Wallpapers/random_wallpaper-1.$ext"
fi

tempDownload="${downloadPath}.tmp"
if ! curl -fsSL --max-time 30 "$link" -o "$tempDownload" 2>/dev/null; then
    echo "Failed to download wallpaper image from $link" >&2
    rm -f "$tempDownload"
    exit 1
fi

mimeType=$(file --mime-type -b "$tempDownload" 2>/dev/null || true)
if [[ "$mimeType" != image/* ]]; then
    echo "Downloaded file is not a valid image (MIME: $mimeType)" >&2
    rm -f "$tempDownload"
    exit 1
fi
mv -f "$tempDownload" "$downloadPath"

# Check if multi-monitor mode is enabled
multiMonitorEnabled=$(jq -r '.background.multiMonitor.enable' "$illogicalImpulseConfigPath" 2>/dev/null)

if [ "$multiMonitorEnabled" == "true" ]; then
    # Get focused monitor
    focusedMonitor=""
    if command -v niri &> /dev/null && niri msg outputs &> /dev/null; then
        focusedMonitor=$(niri msg -j focused-output 2>/dev/null | jq -r '.name // empty' 2>/dev/null)
    elif command -v hyprctl &> /dev/null; then
        focusedMonitor=$(hyprctl monitors -j 2>/dev/null | jq -r '.[] | select(.focused) | .name' 2>/dev/null)
    fi

    if [ -n "$focusedMonitor" ]; then
        # Detect workspace range for this monitor (Niri-specific)
        wsArgs=()
        if command -v niri &> /dev/null && niri msg workspaces &> /dev/null; then
            wsFirst=$(niri msg -j workspaces 2>/dev/null | jq -r --arg monitor "$focusedMonitor" '[.[] | select(.output == $monitor) | .idx] | sort | first // empty' 2>/dev/null)
            wsLast=$(niri msg -j workspaces 2>/dev/null | jq -r --arg monitor "$focusedMonitor" '[.[] | select(.output == $monitor) | .idx] | sort | last // empty' 2>/dev/null)
            if [ -n "$wsFirst" ] && [ -n "$wsLast" ]; then
                wsArgs=(--start-workspace "$wsFirst" --end-workspace "$wsLast")
            fi
        fi
        "$SCRIPT_DIR/../switchwall.sh" --image "$downloadPath" --monitor "$focusedMonitor" "${wsArgs[@]}"
    else
        "$SCRIPT_DIR/../switchwall.sh" --image "$downloadPath"
    fi
else
    "$SCRIPT_DIR/../switchwall.sh" --image "$downloadPath"
fi
