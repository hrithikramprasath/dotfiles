# Configuration inspection — 2026-09-19

## Context

Arch Linux; Niri compositor; systemd-managed iNiR/Quickshell desktop; Kitty/Fish
and Starship; GTK/Qt theming generated from wallpaper colors. Chezmoi deploys
home files and selected QML overlays, while the upstream iNiR installer supplies
the remaining runtime, launcher, Python virtual environment and service wiring.
The pinned upstream revision is `dcba34ee124acb5a191c88b2e1952006fa5afb2f`.

The repository and upstream checkout both had uncommitted work before inspection.
Existing changes were preserved. No packages, commits, pushes or service restarts
are part of these fixes.

## Fixes

- Validate the pinned revision before package installation can change the host.
- Keep installer-owned version and migration ledgers out of chezmoi deployment.
- Keep diff/verify modes from creating bootstrap configuration or symlinks; fail
  explicitly if chezmoi is unavailable. Propagate bootstrap download failures.
- Render Niri virtual-environment paths with the destination home directory.
- Consolidate duplicated login PATH setup in a shared profile and make the iNiR
  environment available to non-interactive login shells. Preserve optional Node
  and pnpm configuration. Guard Zsh interactive initialization.
- Reject a missing KDE color scheme argument instead of looping indefinitely;
  propagate generation failures and replace eval-based path expansion with
  literal expansion, including the legacy literal `$HOME` prefix.
- Select random-wallpaper destinations using Niri's focused-output request.
  Pass monitor names as jq values and workspace arguments as a Bash array.
- Preserve scientific notation in calculator results and reject invalid input
  instead of silently deleting characters and changing the numeric result.
- Document actual restore behavior, runtime ownership and expected theme drift.

## Checks and limits

The regression suite covers restore failure propagation, interrupted installs,
revision validation, read-only inspection, shell profile idempotence, missing
KDE arguments, calculator scientific notation and wallpaper monitor selection.

All 27 QML overlays parsed with Qt qmlformat (without reformatting). JSON/JSONC,
TOML, font XML, Fish and Bash syntax checks passed. An offline chezmoi apply and
verify into an empty temporary home passed; rendered Niri includes validated;
rendered JSON parsed; the Kitty theme link resolved; runtime metadata remained
unmanaged. External font downloads were excluded from this isolated check.

This is a configuration and offline behavior review, not proof of every desktop
interaction. No fresh-machine package installation or visual desktop session was
started. QML parsing does not validate all dynamic bindings or hardware behavior.
Zsh is not installed here, so its interactive startup was not executed. Optional
apps, fonts, network providers and hardware integrations need their dependencies.

The package manifest includes OS packages (both kernel variants and both CPU
microcodes), matching the existing broad restore scope; it was not pruned based
on the current machine. The Fish `auto-Niri.fish` file is outside `conf.d` and is
not automatically sourced; systemd/session startup remains the normal path.

## References

- [Chezmoi script lifecycle](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/): onchange hooks only rerun after rendered content changes.
- [Niri environment configuration](https://niri-wm.github.io/niri/Configuration:-Miscellaneous.html#environment): compositor overrides do not automatically propagate to the user systemd manager.

## Follow-up completion

Live visual verification, cleanup, Autostart remediation and repository synchronization
were subsequently completed; see [the follow-up report](desktop-verification-2026-09-19.md).
