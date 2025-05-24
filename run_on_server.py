import os
import sys
import yaml
import getpass
import subprocess
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication

CONFIG_DIR = os.path.expanduser("~/.config/RunOnServer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "servers.yaml")

def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        default_config = {
            'servers': [
                {
                    'name': 'Localhost',
                    'host': 'localhost',
                    'user': getpass.getuser(),
                    'category': 'Default',
                    'commands': [
                        {
                            'name': 'Dateien anzeigen',
                            'command': 'ls ~/',
                            'hold_terminal': True
                        }
                    ]
                }
            ],
            'global_commands': [],
            'category_commands': {}
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f)

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def execute_ssh_command(user, host, command, hold):
    terminal_cmd = [
        "konsole",
        "-e",
        f"bash -c 'ssh {user}@{host} "{command}"; {'bash' if hold else 'exit'}'"
    ]
    subprocess.Popen(terminal_cmd)

def execute_group_command(servers, category, command, hold):
    for server in servers:
        if server.get('category') == category:
            execute_ssh_command(server['user'], server['host'], command, hold)

def create_tray_icon():
    ensure_config_exists()
    config = load_config()

    app = QApplication(sys.argv)
    tray = QSystemTrayIcon(QIcon.fromTheme("network-server"), parent=app)
    menu = QMenu()

    servers_by_category = {}
    for server in config.get('servers', []):
        category = server.get('category', 'Uncategorized')
        servers_by_category.setdefault(category, []).append(server)

    for category, servers in servers_by_category.items():
        category_menu = QMenu(category, menu)

        # Kategorie-Befehle
        for group_cmd in config.get('category_commands', {}).get(category, []):
            action = QAction(f"[{category}] {group_cmd['name']}")
            action.triggered.connect(lambda checked=False, c=group_cmd, cat=category: execute_group_command(
                config['servers'], cat, c['command'], c.get('hold_terminal', True)
            ))
            category_menu.addAction(action)

        category_menu.addSeparator()

        for server in servers:
            server_menu = QMenu(server['name'], category_menu)
            for cmd in server.get('commands', []):
                action = QAction(cmd['name'])
                action.triggered.connect(lambda checked=False, s=server, c=cmd: execute_ssh_command(
                    s['user'], s['host'], c['command'], c.get('hold_terminal', True)
                ))
                server_menu.addAction(action)
            category_menu.addMenu(server_menu)

        menu.addMenu(category_menu)

    if 'global_commands' in config:
        global_menu = QMenu("Global Commands", menu)
        for cmd in config['global_commands']:
            action = QAction(cmd['name'])
            action.triggered.connect(lambda checked=False, c=cmd: [
                execute_ssh_command(s['user'], s['host'], c['command'], c.get('hold_terminal', True))
                for s in config.get('servers', [])
            ])
            global_menu.addAction(action)
        menu.addMenu(global_menu)

    menu.addSeparator()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(QCoreApplication.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.setToolTip("RunOnServer")
    tray.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    create_tray_icon()
