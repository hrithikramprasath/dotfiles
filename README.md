# Dotfiles

Personal configurations for Arch Linux with **Niri** (Wayland scrollable tiling compositor) and **iNiR** (Quickshell desktop shell), managed with **[Chezmoi](https://www.chezmoi.io/)**.

## 📸 Desktop Showcase

| Desktop & Right Control Panel | Widgets Panel & Typography |
| :---: | :---: |
| ![Right Sidebar](assets/screenshots/01-desktop-right-sidebar.png) | ![Widgets Panel](assets/screenshots/02-left-widgets-panel.png) |

| Expanded Pill Status Bar | Hardware Monitor Dropdown |
| :---: | :---: |
| ![Expanded Pill Bar](assets/screenshots/03-expanded-pill-bar.png) | ![System Monitor](assets/screenshots/04-system-monitor-dropdown.png) |

## Repository Architecture

```
.
├── dot_config/           # Managed configuration directory (~/.config)
│   ├── niri/             # Niri compositor config, modular rules & keybinds
│   ├── inir/             # iNiR Quickshell shell preferences, themes & actions
│   ├── kitty/            # Kitty terminal configuration & themes
│   ├── fish/             # Fish shell config, aliases & environment
│   ├── starship.toml     # Starship prompt configuration
│   ├── fastfetch/        # Fastfetch system info styling
│   ├── cava/             # Cava audio visualizer
│   ├── matugen/          # Material You dynamic wallpaper theming
│   ├── Kvantum/          # Kvantum Qt style config
│   ├── qt6ct/            # Qt6 settings & styling
│   ├── gtk-3.0/          # GTK3 theme, font, icon settings
│   ├── gtk-4.0/          # GTK4 theme, font, icon settings
│   ├── darklyrc          # Darkly Qt widget style options
│   ├── fontconfig/       # Font configurations
│   ├── xdg-desktop-portal/ # Wayland portal routing for Niri
│   ├── chrome-flags.conf # Wayland & ozone flags for Google Chrome
│   └── code-flags.conf   # Wayland flags for VS Code
├── .chezmoiscripts/      # Automated lifecycle hooks
│   └── run_onchange_before_install-packages.sh.tmpl  # Auto package sync on change
├── packages-repo.txt     # Core OS, Niri & iNiR official dependencies
├── packages-aur.txt      # Core UI, font, theme & shell AUR packages
├── packages-apps.txt     # Optional user applications (Brave, Discord, Spotify, Steam, etc.)
├── .chezmoiignore        # Files excluded from target deployment
├── .gitignore
├── install.sh            # Universal bootstrap & synchronization wrapper
└── README.md
```

## Key Applications & Stack

* **Compositor**: Niri (Scrollable tiling Wayland compositor)
* **Desktop Shell**: iNiR (Quickshell / Qt6 QML interface)
* **Terminal**: Kitty
* **Shell Environment**: Fish + Starship
* **Browser**: User choice (Brave, Chrome, Firefox, etc.) via XDG / `Super+W`
* **Media Player**: mpv + mpv-mpris
* **Screen Recorder**: wf-recorder & ffmpeg
* **Snipping & OCR**: iNiR Region Tool (grim + slurp + swappy + tesseract)
* **Color Picker**: hyprpicker
* **App Launcher**: iNiR Overview (`Mod+Space`)

## Installation & System Recovery

### Option 1: One-Line Remote Bootstrap (Any Fresh Machine)
On a brand new Arch installation, run:

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply hrithikramprasath
```
This single command will:
1. Download and install `chezmoi`
2. Clone this repository to `~/.local/share/chezmoi`
3. Execute package installation hooks for official and AUR packages
4. Deploy and validate all `.config` directories

### Option 2: Clone & Local Script
If you prefer running via git clone:

```bash
git clone https://github.com/hrithikramprasath/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh --full
```

### Options for `./install.sh`:
* `./install.sh` / `./install.sh --configs-only`: Apply configurations only (instant).
* `./install.sh --full`: Full system sync (installs packages if manifests changed + applies configs).
* `./install.sh --diff`: Preview line-by-line differences between repo and local files.
* `./install.sh --verify`: Check for configuration drift (exits 0 if clean).

> [!NOTE]
> **Minimal & Bloat-Free by Design**: The automated installation provisions **only** the required OS components, Niri compositor, iNiR shell widgets, fonts, themes, and system tools needed to run this exact desktop environment seamlessly. Personal user applications (such as browsers, Discord, Spotify, Steam, and VS Code) are decoupled into [`packages-apps.txt`](packages-apps.txt). If you wish to install your full app suite on a machine, run:
> ```bash
> yay -S --needed - < packages-apps.txt
> ```

## Daily Workflow with Chezmoi

```bash
# Edit any configuration safely (auto-applies when editor closes)
chezmoi edit ~/.config/niri/config.kdl

# Check differences between your repository and active files
chezmoi diff

# Apply changes from repository to active system
chezmoi apply

# Check for unmanaged drift
chezmoi verify

# Enter repository directory directly
chezmoi cd
```

## License

This project is licensed under the [MIT License](LICENSE).
Copyright (c) 2026 Hrithik Ram Prasath. Anyone using, copying, or distributing these configurations must retain the original copyright and permission notice.
