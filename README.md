# RunOnServer

**RunOnServer** is a Linux system tray application that lets you manage multiple remote servers via SSH. You can view server status, run commands on individual servers or on all at once, and use a configuration file to define actions.

## Features

- System tray icon with menu
- Per-server status (online/offline)
- Execute commands on individual servers
- Run global commands on all servers
- Configure via `servers.yaml` file
- Automatic SSH key generation and setup
- Terminal window holds output if needed
- Compatible with KDE, GNOME, XFCE, and more

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pekas1969/RunOnServer.git
   cd RunOnServer
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python run_on_server.py
   ```

## Configuration

The configuration file is located at:
```
~/.config/RunOnServer/servers.yaml
```

If the file does not exist, it will be created on first run with a default `localhost` entry.

### Example `servers.yaml`

```yaml
servers:
  - name: "Webserver"
    host: "192.168.1.100"
    user: "root"
    commands:
      - name: "Restart Apache"
        command: "sudo systemctl restart apache2"
        hold_terminal: true

global_commands:
  - name: "Update All Systems"
    command: "sudo dnf upgrade -y || sudo apt update && sudo apt upgrade -y || sudo pacman -Syu --noconfirm || sudo zypper dup -y"
    hold_terminal: true
```

## Notes

- SSH keys are stored under `~/.ssh/`. The app generates a key if not present.
- If you use GitHub, make sure to push code using SSH or a personal access token.
- Tested under Python 3.10+ and PyQt6.

## License

MIT License
