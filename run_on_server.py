import sys
import subprocess
import os
import shutil
import threading
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
import yaml
import socket
import getpass

CONFIG_DIR = os.path.expanduser("~/.config/RunOnServer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "servers.yaml")

# Funktion zum Einlesen der YAML-Datei, legt Default an, falls nicht vorhanden
def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        default_user = getpass.getuser()
        default_config = {
            "servers": [
                {
                    "name": "Server 1",
                    "host": "192.168.177.5",
                    "user": "root",
                    "category": "Servers-Home",
                    "commands": [
                        {
                            "name": "Apache neu starten",
                            "command": "sudo systemctl restart apache2",
                            "hold_terminal": True
                        }
                    ]
                },
                {
                    "name": "Server 2",
                    "host": "192.168.177.11",
                    "user": "root",
                    "category": "Servers-Home",
                    "commands": [
                        {
                            "name": "Nginx neu starten",
                            "command": "sudo systemctl restart nginx",
                            "hold_terminal": True
                        }
                    ]
                },
                {
                    "name": "Server 3",
                    "host": "192.168.177.200",
                    "user": default_user,
                    "category": "Servers-Work",
                    "commands": [
                        {
                            "name": "Neustarten",
                            "command": "sudo reboot",
                            "hold_terminal": False
                        },
                        {
                            "name": "Inhalt anzeigen",
                            "command": "ls",
                            "hold_terminal": True
                        }
                    ]
                }
            ],
            "category_commands": {
                "Servers-Home": [
                    {
                        "name": "Neustarten",
                        "command": "sudo reboot",
                        "hold_terminal": False
                    }
                ],
                "Servers-Work": [
                    {
                        "name": "Daten sichern",
                        "command": "rsync -av ~/daten/ /backup/",
                        "hold_terminal": True
                    }
                ]
            },
            "global_commands": [
                {
                    "name": "System aktualisieren",
                    "command": "sudo apt update && sudo apt upgrade -y",
                    "hold_terminal": True
                }
            ]
        }
        with open(path, "w") as f:
            yaml.dump(default_config, f)
        return default_config
    else:
        with open(path, "r") as file:
            return yaml.safe_load(file)

# Prüfen, ob Host online ist
def is_host_online(host):
    try:
        socket.setdefaulttimeout(1.5)
        socket.create_connection((host, 22))
        return True
    except Exception:
        return False

# SSH-Key Pfad
def get_ssh_key_path():
    return os.path.expanduser("~/.ssh/id_rsa.pub")

def ssh_key_exists():
    return os.path.exists(get_ssh_key_path())

def generate_ssh_key():
    if not ssh_key_exists():
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", os.path.expanduser("~/.ssh/id_rsa")])

def copy_ssh_key_to_server(user, host):
    subprocess.run(["ssh-copy-id", f"{user}@{host}"])

# Terminalbefehl ausführen
def run_ssh_command(server, command):
    user = server["user"]
    host = server["host"]
    remote_cmd = command["command"]
    hold = command.get("hold_terminal", False)

    if shutil.which("konsole"):
        term_cmd = ["konsole", "-e"]
    elif shutil.which("gnome-terminal"):
        term_cmd = ["gnome-terminal", "--"]
    elif shutil.which("xfce4-terminal"):
        term_cmd = ["xfce4-terminal", "-e"]
    elif shutil.which("x-terminal-emulator"):
        term_cmd = ["x-terminal-emulator", "-e"]
    else:
        QMessageBox.warning(None, "Fehler", "Kein unterstütztes Terminal gefunden.")
        return

    # Bash-Befehl mit ssh, bei hold Terminal offen lassen
    bash_cmd = f"ssh {user}@{host} '{remote_cmd}'"
    if hold:
        bash_cmd += "; echo 'Press any key to close...'; read -n 1"

    subprocess.Popen(term_cmd + ["bash", "-c", bash_cmd])

# Klick Handler für einzelne Befehle
def on_command_click(server, command):
    threading.Thread(target=run_ssh_command, args=(server, command), daemon=True).start()

# Klick Handler für globale Befehle (für alle Server)
def on_global_command_click(config, command):
    for server in config.get("servers", []):
        threading.Thread(target=run_ssh_command, args=(server, command), daemon=True).start()

# Menü bauen mit Kategorien
def build_menu(tray_icon, config):
    menu = QMenu()

    # Global Commands als eigener Menüpunkt "Alle Server"
    global_commands = config.get("global_commands", [])
    if global_commands:
        global_menu = menu.addMenu("Alle Server")
        for command in global_commands:
            global_menu.addAction(command["name"], lambda c=command: on_global_command_click(config, c))
        menu.addSeparator()

    # Server nach Kategorien gruppieren
    servers = config.get("servers", [])
    category_commands = config.get("category_commands", {})

    # Kategorien aus Servern extrahieren (ohne Duplikate)
    categories = sorted(set(s.get("category", "Unkategorisiert") for s in servers))

    for category in categories:
        category_menu = menu.addMenu(category)

        # Kategorie-spezifische Befehle hinzufügen
        cat_cmds = category_commands.get(category, [])
        if cat_cmds:
            for command in cat_cmds:
                # Lambda mit default-Argument zum Einfangen von command nötig wegen late binding
                category_menu.addAction(command["name"], lambda c=command: on_global_command_click(
                    {"servers": [s for s in servers if s.get("category") == category]}, c))
            category_menu.addSeparator()

        # Server der Kategorie hinzufügen
        for server in [s for s in servers if s.get("category") == category]:
            server_name = server["name"]
            host = server["host"]
            online = is_host_online(host)
            status_text = f"{server_name} ({'online' if online else 'offline'})"

            server_menu = category_menu.addMenu(status_text)

            for command in server.get("commands", []):
                server_menu.addAction(command["name"], lambda s=server, c=command: on_command_click(s, c))

            server_menu.addSeparator()
            ssh_action = QAction("SSH-Key einrichten", server_menu)
            ssh_action.triggered.connect(lambda checked, s=server: setup_ssh_key(s))
            server_menu.addAction(ssh_action)

    menu.addSeparator()
    menu.addAction("Beenden", QApplication.instance().quit)
    tray_icon.setContextMenu(menu)

# SSH-Key Setup Workflow
def setup_ssh_key(server):
    generate_ssh_key()
    user = server["user"]
    host = server["host"]
    copy_ssh_key_to_server(user, host)
    QMessageBox.information(None, "SSH-Key", f"SSH-Key für {user}@{host} eingerichtet.")

def main():
    app = QApplication(sys.argv)
    config = load_config()

    tray_icon = QSystemTrayIcon(QIcon.fromTheme("network-server"), app)
    tray_icon.setToolTip("RunOnServer")

    build_menu(tray_icon, config)
    tray_icon.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
