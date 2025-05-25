# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.0.2-0] - 2025-05-25

### Added
- Full support for editing the `servers.yaml` configuration through a graphical interface.
- Added functionality to **create, edit, and delete servers**, including name, host, user, and category.
- Servers can now be **moved to another category** or **cloned** into a new entry via context menu.
- Added support for **editing, adding, and deleting commands**:
  - **Per server**: Manage individual SSH commands.
  - **Per category (group commands)**: Manage shared commands for server groups.
  - **Global commands**: Manage commands that apply to all servers.
- Context menus dynamically adjust based on item type (server, category, command).
- Improved tree structure to clearly separate global commands, category commands, and servers.
- Added user-friendly input dialogs for command and server editing.

### Changed
- Internal structure refactored to improve maintainability and ensure category-command consistency.

### Fixed
- Tree view now fully updates after every change to reflect the current state of the YAML file.
- Resolved missing context menu behavior on server and command items.

---

## [v0.0.2-0] - 2025-05-23

### Added
- ✨ Support for categorizing servers into groups (e.g., `Servers-Home`, `Servers-Work`) via `servers.yaml`
- ➕ Support for sending global commands to all servers within a group
- 🚀 New startup script `runonserver_start.sh` that activates the virtual environment and runs the app

### Changed
- 📄 Updated `README.md` with new usage instructions and group-based configuration

## What's new in v0.0.2-0

- feat: add support for categories with group-specific commands
- feat: allow category-wide and global commands via YAML
- fix: QIcon import issue (system tray icon)
- docs: simplified README for non-virtual environment installation
- chore: updated changelog and minor cleanups

---

## [v0.0.1-0] - 2025-05-22

### Added
- Initial implementation of **RunOnServer**.
- System tray icon for Linux (KDE, GNOME, XFCE...).
- Server status check (online/offline).
- Per-server command execution via SSH.
- Per-command terminal control (`hold_terminal` support).
- Global commands for running a command on all servers.
- Automatic creation of default `servers.yaml` in `~/.config/RunOnServer/` if missing.
- SSH key generation and automatic upload (`ssh-copy-id`) if needed.

### Notes
- This version is **experimental** and intended for personal use or testing.
- Compatible with modern Linux distributions.
- Terminal detection supports `konsole`, `gnome-terminal`, `xfce4-terminal`, `x-terminal-emulator`.

---

## [0.0.1-1] - 2025-05-22

### Fixed
- Updated contact email address in README.md to `peter.kasparak@gmail.com`.

---
