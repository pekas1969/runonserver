# RunOnServer

RunOnServer is a lightweight Linux system tray application to manage and run commands via SSH on multiple servers, configured via a YAML file.

---

## Features

- System tray icon showing server statuses (online/offline)
- Per-server command menus executed via SSH in terminal windows
- Support for multiple commands per server
- Global commands executed on all servers simultaneously
- Automatic SSH key generation and setup per server
- Configurable behavior to keep terminal windows open after command execution
- Works primarily on KDE Plasma 6, but compatible with GNOME, XFCE, and others

---

## Installation & Setup

1. **Install dependencies**

```bash
pip install PyQt6 PyYAML
```

2. **Place `servers.yaml` in `~/.config/RunOnServer/`**

On first run, if no config is found, a default one with a localhost entry is created automatically.

3. **Run the application**

```bash
python3 run_on_server.py
```

---

## Configuration File Example (`servers.yaml`)

```yaml
servers:
  - name: "Webserver"
    host: "192.168.177.5"
    user: "root"
    commands:
      - name: "Restart Apache"
        command: "sudo systemctl restart apache2"
        hold_terminal: true

  - name: "Fileserver"
    host: "192.168.177.200"
    user: "peter"
    commands:
      - name: "Reboot"
        command: "sudo reboot"
        hold_terminal: false
      - name: "List directory"
        command: "ls"
        hold_terminal: true

global_commands:
  - name: "Update system"
    command: "sudo dnf upgrade -y || sudo apt update && sudo apt upgrade -y || sudo pacman -Syu --noconfirm || sudo zypper dup -y"
    hold_terminal: true
```

---

## How to Remove RunOnServer

If you want to uninstall and remove RunOnServer from your system, follow these steps:

1. **Remove the application files**

Delete the directory where you cloned or placed the `run_on_server.py` script and related files.

```bash
rm -rf /path/to/RunOnServer
```

Replace `/path/to/RunOnServer` with the actual path where the project is located.

2. **Remove the configuration directory**

Delete the config folder with your server configurations:

```bash
rm -rf ~/.config/RunOnServer
```

3. **(Optional) Remove the Python virtual environment**

If you used a virtual environment for dependencies, remove it as well:

```bash
rm -rf /path/to/your/venv
```

Replace `/path/to/your/venv` with your virtual environment folder.

4. **(Optional) Uninstall Python dependencies**

If you installed dependencies globally (not recommended), you can uninstall them:

```bash
pip uninstall PyQt6 PyYAML
```

---

## Contributing

Feel free to open issues or submit pull requests on GitHub.

---

## License

[MIT License](LICENSE)

---

## Contact

For questions or suggestions, open an issue on GitHub or contact peter.kasparak@gmail.com
