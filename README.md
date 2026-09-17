# Dotfiles

Personal configurations for Arch Linux with **Niri** (Wayland scrollable tiling compositor) and **iNiR** (Quickshell desktop shell).

## Components & Structure

```
.
├── .config/
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
│   ├── mimeapps.list     # Default application associations
│   ├── chrome-flags.conf # Wayland & ozone flags for Google Chrome
│   └── code-flags.conf   # Wayland flags for VS Code
├── .gitignore
├── install.sh            # Deployment / symlinking script
└── README.md
```

## Key Applications

* **Compositor**: Niri
* **Shell**: iNiR (Quickshell)
* **Terminal**: Kitty
* **Shell Environment**: Fish + Starship
* **Browser**: Google Chrome
* **Media Player**: mpv + mpv-mpris
* **Screen Recorder**: wf-recorder
* **Snipping Tool**: iNiR Region Tool (grim + slurp + swappy)
* **Color Picker**: hyprpicker
* **App Launcher**: iNiR Overview (`Mod+Space`)

## Installation

To deploy these dotfiles on a fresh setup:

```bash
git clone https://github.com/hrithikramprasath/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

## License

This project is licensed under the [MIT License](LICENSE).
Copyright (c) 2026 Hrithik Ram Prasath. Anyone using, copying, or distributing these configurations must retain the original copyright and permission notice.

