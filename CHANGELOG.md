# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
