import os
import sys
import yaml
import subprocess
import getpass
import shutil
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "RunOnServer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "servers.yaml")


def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        default_user = getpass.getuser()
        default_config = {
            "servers": [
                {
                    "name": "Localhost",
                    "host": "localhost",
                    "user": default_user,
                    "commands": [
                        {
                            "name": "List files",
                            "command": "ls ~/",
                            "hold_terminal": True
                        }
                    ],
                    "category": "Default"
                }
            ],
            "global_commands": [],
            "category_commands": {}
        }
        with open(path, "w") as f:
            yaml.dump(default_config, f)
        return default_config
    else:
        with open(path, "r") as file:
            return yaml.safe_load(file)


def open_interactive_terminal(server):
    user = server["user"]
    host = server["host"]

    if shutil.which("konsole"):
        term_cmd = ["konsole", "-e", f"ssh {user}@{host}"]
    elif shutil.which("gnome-terminal"):
        term_cmd = ["gnome-terminal", "--", "ssh", f"{user}@{host}"]
    elif shutil.which("xfce4-terminal"):
        term_cmd = ["xfce4-terminal", "-e", f"ssh {user}@{host}"]
    elif shutil.which("x-terminal-emulator"):
        term_cmd = ["x-terminal-emulator", "-e", f"ssh {user}@{host}"]
    else:
        QMessageBox.warning(None, "Error", "No supported terminal emulator found.")
        return

    subprocess.Popen(term_cmd)


def run_command(command, hold_terminal):
    if shutil.which("konsole"):
        cmd = ["konsole", "-e", "bash", "-c", f"{command}; {'exec bash' if hold_terminal else ''}"]
    elif shutil.which("gnome-terminal"):
        cmd = ["gnome-terminal", "--", "bash", "-c", f"{command}; {'exec bash' if hold_terminal else ''}"]
    elif shutil.which("xfce4-terminal"):
        cmd = ["xfce4-terminal", "-e", f"bash -c '{command}; {'exec bash' if hold_terminal else ''}'"]
    elif shutil.which("x-terminal-emulator"):
        cmd = ["x-terminal-emulator", "-e", f"bash -c '{command}; {'exec bash' if hold_terminal else ''}'"]
    else:
        QMessageBox.warning(None, "Error", "No supported terminal emulator found.")
        return

    subprocess.Popen(cmd)


def build_menu(tray_icon, config):
    menu = QMenu()

    # Global commands
    for cmd in config.get("global_commands", []):
        menu.addAction(f"🌐 {cmd['name']}", lambda c=cmd: run_command(c["command"], c.get("hold_terminal", False)))

    menu.addSeparator()

    # Sort servers by category
    categories = {}
    for server in config.get("servers", []):
        category = server.get("category", "Uncategorized")
        categories.setdefault(category, []).append(server)

    for category, servers_in_category in categories.items():
        category_menu = menu.addMenu(category)

        # Category commands
        for cmd in config.get("category_commands", {}).get(category, []):
            category_menu.addAction(f"📁 {cmd['name']}", lambda c=cmd: run_command(c["command"], c.get("hold_terminal", False)))

        category_menu.addSeparator()

        for server in servers_in_category:
            server_menu = category_menu.addMenu(server["name"])

            # Add interactive terminal option
            server_menu.addAction("🖥️ Terminal öffnen", lambda s=server: open_interactive_terminal(s))

            for cmd in server.get("commands", []):
                server_menu.addAction(cmd["name"], lambda c=cmd: run_command(c["command"], c.get("hold_terminal", False)))

    menu.addSeparator()
    menu.addAction("Quit", QApplication.instance().quit)
    tray_icon.setContextMenu(menu)


def main():
    app = QApplication(sys.argv)
    tray_icon = QSystemTrayIcon(QIcon.fromTheme("network-server"))
    tray_icon.setToolTip("RunOnServer")
    tray_icon.show()

    config = load_config()
    build_menu(tray_icon, config)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
