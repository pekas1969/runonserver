import sys
import subprocess
import os
import shutil
import threading
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
import yaml
import socket
import getpass  # Für aktuellen Usernamen

CONFIG_DIR = os.path.expanduser("~/.config/RunOnServer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "servers.yaml")

# Standard-Config als Python-Dict
DEFAULT_CONFIG = {
    "servers": [
        {
            "name": "Localhost",
            "host": "localhost",
            "user": getpass.getuser(),
            "commands": [
                {
                    "name": "Dateien anzeigen",
                    "command": "ls ~/",
                    "hold_terminal": True
                }
            ]
        }
    ]
}

def create_default_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f)
    print(f"Standard-Konfig erstellt unter {CONFIG_PATH}")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        create_default_config()
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)

def is_host_online(host):
    try:
        socket.setdefaulttimeout(1.5)
        socket.create_connection((host, 22))
        return True
    except Exception:
        return False

def get_ssh_key_path():
    return os.path.expanduser("~/.ssh/id_rsa.pub")

def ssh_key_exists():
    return os.path.exists(get_ssh_key_path())

def generate_ssh_key():
    if not ssh_key_exists():
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", os.path.expanduser("~/.ssh/id_rsa")])

def copy_ssh_key_to_server(user, host):
    subprocess.run(["ssh-copy-id", f"{user}@{host}"])

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

    full_cmd = f"ssh {user}@{host} '{remote_cmd}'"
    if hold:
        full_cmd += "; echo 'Drücke eine Taste zum Schließen...'; read -n 1"

    subprocess.Popen(term_cmd + ["bash", "-c", full_cmd])

def on_command_click(server, command):
    threading.Thread(target=run_ssh_command, args=(server, command), daemon=True).start()

def on_global_command_click(config, command):
    for server in config.get("servers", []):
        threading.Thread(target=run_ssh_command, args=(server, command), daemon=True).start()

def build_menu(tray_icon, config):
    menu = QMenu()

    global_commands = config.get("global_commands", [])
    if global_commands:
        global_menu = menu.addMenu("Alle Server")
        for command in global_commands:
            global_menu.addAction(command["name"], lambda c=command: on_global_command_click(config, c))
        menu.addSeparator()

    for server in config.get("servers", []):
        server_name = server["name"]
        host = server["host"]
        online = is_host_online(host)
        status_text = f"{server_name} ({'online' if online else 'offline'})"

        server_menu = menu.addMenu(status_text)

        for command in server.get("commands", []):
            server_menu.addAction(command["name"], lambda s=server, c=command: on_command_click(s, c))

        server_menu.addSeparator()
        ssh_action = QAction("SSH-Key einrichten", server_menu)
        ssh_action.triggered.connect(lambda checked, s=server: setup_ssh_key(s))
        server_menu.addAction(ssh_action)

    menu.addSeparator()
    menu.addAction("Beenden", QApplication.instance().quit)
    tray_icon.setContextMenu(menu)

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
