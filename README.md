# RunOnServer

**RunOnServer** is a system tray application for Linux that allows you to manage and execute commands on remote servers via SSH.  
**RunOnServer Editor** is a graphical YAML editor to easily manage your server list and command configuration.

## ✨ Features

- Display a list of remote servers grouped by category
- Check online status of servers (ping/port 22)
- Execute custom SSH commands on individual servers
- Execute group-specific or global commands across multiple servers
- Automatically hold terminal window open if needed
- Setup SSH key authentication via GUI
- Open direct SSH terminal to any configured server
- Configuration via a simple `servers.yaml` file
- Tree-based GUI editor to:
  - Add/edit/delete servers
  - Add/edit/delete commands (server, group, global)
  - Clone or move servers between categories
  - Manage everything without manually editing YAML

## 🛠️ Installation (without virtual environment)

Install the required dependencies:

```bash
sudo apt install python3 python3-pip
pip3 install PyQt6 pyyaml
```

Clone this repository:

```bash
git clone https://github.com/pekas1969/RunOnServer.git
cd RunOnServer
```

## 🚀 Launch

To start the system tray application:

```bash
python3 run_on_server.py
or
./runonserver_start.sh
```

To start the graphical configuration editor:

```bash
./runonserver_editor.sh
```

If not executable, run:

```bash
chmod +x runonserver_start.sh runonserver_editor.sh
```

## 🧾 Configuration file: `servers.yaml`

Located at `~/.config/RunOnServer/servers.yaml`.

### Structure example:

```yaml
servers:
  - name: "Webserver"
    host: "192.168.177.5"
    user: "root"
    category: "Servers-Home"
    commands:
      - name: "Restart Apache"
        command: "sudo systemctl restart apache2"
        hold_terminal: true

  - name: "File Server"
    host: "192.168.177.200"
    user: "admin"
    category: "Servers-Work"
    commands:
      - name: "Show contents"
        command: "ls -la"
        hold_terminal: true

category_commands:
  "Servers-Home":
    - name: "Reboot all Home Servers"
      command: "sudo reboot"
      hold_terminal: false

  "Servers-Work":
    - name: "Backup data"
      command: "rsync -av ~/data /backup/"
      hold_terminal: true

global_commands:
  - name: "Update system"
    command: "sudo apt update && sudo apt upgrade -y"
    hold_terminal: true
```

You can edit this file manually or via the **RunOnServer Editor** GUI.

## 📁 Desktop Integration (optional)

Use the install script to create `.desktop` launchers for menu integration:

```bash
./install_desktop_entries.sh
```

## 📬 Contact

**Author**: Peter Kaspar  
**GitHub**: [github.com/pekas1969](https://github.com/pekas1969)  
**Email**: kaspar@limbic-media.de

---

Licensed under MIT License.
