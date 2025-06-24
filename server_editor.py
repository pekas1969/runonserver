import sys
import os
import yaml
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QInputDialog, QLineEdit, QMessageBox,
    QMenu, QDialog, QDialogButtonBox, QLabel, QFormLayout, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt

CONFIG_PATH = os.path.expanduser("~/.config/RunOnServer/servers.yaml")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"servers": [], "global_commands": [], "category_commands": {}}
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(data, f)

class CommandDialog(QDialog):
    def __init__(self, parent=None, command=None):
        super().__init__(parent)
        self.setWindowTitle("Befehl bearbeiten" if command else "Befehl hinzufügen")
        self.command = command or {"name": "", "command": "", "hold_terminal": False}
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit(self.command["name"])
        self.cmd_input = QTextEdit(self.command["command"])
        self.hold_input = QComboBox()
        self.hold_input.addItems(["false", "true"])
        self.hold_input.setCurrentIndex(1 if self.command.get("hold_terminal") else 0)

        layout.addRow("Name:", self.name_input)
        layout.addRow("Befehl:", self.cmd_input)
        layout.addRow("Terminal offen halten:", self.hold_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_result(self):
        return {
            "name": self.name_input.text(),
            "command": self.cmd_input.toPlainText(),
            "hold_terminal": self.hold_input.currentText() == "true"
        }

class ServerDialog(QDialog):
    def __init__(self, parent=None, server=None, categories=None):
        super().__init__(parent)
        self.setWindowTitle("Server bearbeiten" if server else "Server hinzufügen")
        self.server = server or {"name": "", "host": "", "user": "", "category": ""}
        self.categories = categories or []
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit(self.server["name"])
        self.host_input = QLineEdit(self.server["host"])
        self.user_input = QLineEdit(self.server["user"])
        self.cat_input = QComboBox()
        self.cat_input.addItems(self.categories)
        if self.server["category"] in self.categories:
            self.cat_input.setCurrentText(self.server["category"])

        layout.addRow("Name:", self.name_input)
        layout.addRow("Host:", self.host_input)
        layout.addRow("User:", self.user_input)
        layout.addRow("Kategorie:", self.cat_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_result(self):
        return {
            "name": self.name_input.text(),
            "host": self.host_input.text(),
            "user": self.user_input.text(),
            "category": self.cat_input.currentText(),
            "commands": self.server.get("commands", [])
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RunOnServer Editor")
        self.resize(600, 500)
        self.data = load_config()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name"])
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)
        self.setCentralWidget(self.tree)

        self.build_tree()

    def build_tree(self):
        self.tree.clear()

        # Globale Befehle
        global_item = QTreeWidgetItem(["Globale Befehle"])
        self.tree.addTopLevelItem(global_item)
        for cmd in self.data.get("global_commands", []):
            QTreeWidgetItem(global_item, [cmd["name"]])

        # Kategorie-spezifische Befehle + Server
        categories = {}
        for server in self.data.get("servers", []):
            cat = server.get("category", "Unkategorisiert")
            if cat not in categories:
                cat_item = QTreeWidgetItem([cat])
                self.tree.addTopLevelItem(cat_item)
                categories[cat] = cat_item

                # Kategorie-Befehle
                for cmd in self.data.get("category_commands", {}).get(cat, []):
                    QTreeWidgetItem(cat_item, [f"[Gruppe] {cmd['name']}"])

            server_item = QTreeWidgetItem([server["name"]])
            server_item.setData(0, Qt.ItemDataRole.UserRole, server)
            categories[cat].addChild(server_item)

            for cmd in server.get("commands", []):
                QTreeWidgetItem(server_item, [cmd["name"]])

    def open_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return

        menu = QMenu()
        parent = item.parent()

        if parent and parent.parent():  # Serverbefehl
            menu.addAction("Edit command", lambda: self.edit_command(parent, item))
            menu.addAction("Delete command", lambda: self.delete_command(parent, item))
        elif parent:  # Server
            menu.addAction("New Server", lambda: self.add_server(item))
            menu.addAction("Edit server", lambda: self.edit_server(item))
            menu.addAction("Delete server", lambda: self.delete_server(item))
            menu.addAction("New command", lambda: self.add_command(item))
            menu.addAction("Clone server", lambda: self.clone_server(item))
            menu.addAction("Move server", lambda: self.move_server(item))
        elif item.text(0) == "Global commands":
            menu.addAction("New global command", self.add_global_command)
        elif item.text(0) in self.data.get("category_commands", {}):  # Kategorie
            menu.addAction("New group command", lambda: self.add_category_command(item))
            menu.addAction("Edit group command", lambda: self.edit_category_command(item))
            menu.addAction("Delete group command", lambda: self.delete_category_command(item))

        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def find_server(self, name):
        return next((s for s in self.data["servers"] if s["name"] == name), None)

    def add_server(self, cat_item):
        dialog = ServerDialog(self, categories=self.data["category_commands"].keys())
        if dialog.exec():
            new_server = dialog.get_result()
            self.data["servers"].append(new_server)
            save_config(self.data)
            self.build_tree()

    def edit_server(self, item):
        server = self.find_server(item.text(0))
        if server:
            dialog = ServerDialog(self, server=server, categories=self.data["category_commands"].keys())
            if dialog.exec():
                updated = dialog.get_result()
                index = self.data["servers"].index(server)
                self.data["servers"][index] = updated
                save_config(self.data)
                self.build_tree()

    def delete_server(self, item):
        server = self.find_server(item.text(0))
        if server and QMessageBox.question(self, "Löschen", "Diesen Server löschen?") == QMessageBox.StandardButton.Yes:
            self.data["servers"].remove(server)
            save_config(self.data)
            self.build_tree()

    def clone_server(self, item):
        server = self.find_server(item.text(0))
        if not server:
            return
        clone = server.copy()
        clone["name"] += " (Kopie)"
        dialog = ServerDialog(self, server=clone, categories=self.data["category_commands"].keys())
        if dialog.exec():
            self.data["servers"].append(dialog.get_result())
            save_config(self.data)
            self.build_tree()

    def move_server(self, item):
        server = self.find_server(item.text(0))
        if not server:
            return
        new_cat, ok = QInputDialog.getItem(self, "Kategorie wählen", "Neue Kategorie:", list(self.data["category_commands"].keys()), editable=False)
        if ok and new_cat != server["category"]:
            server["category"] = new_cat
            save_config(self.data)
            self.build_tree()

    def add_command(self, server_item):
        server = self.find_server(server_item.text(0))
        if server:
            dialog = CommandDialog(self)
            if dialog.exec():
                server["commands"].append(dialog.get_result())
                save_config(self.data)
                self.build_tree()

    def edit_command(self, server_item, cmd_item):
        server = self.find_server(server_item.text(0))
        cmd_name = cmd_item.text(0)
        if server:
            cmd = next((c for c in server["commands"] if c["name"] == cmd_name), None)
            if cmd:
                dialog = CommandDialog(self, command=cmd)
                if dialog.exec():
                    index = server["commands"].index(cmd)
                    server["commands"][index] = dialog.get_result()
                    save_config(self.data)
                    self.build_tree()

    def delete_command(self, server_item, cmd_item):
        server = self.find_server(server_item.text(0))
        cmd_name = cmd_item.text(0)
        if server and QMessageBox.question(self, "Löschen", "Diesen Befehl löschen?") == QMessageBox.StandardButton.Yes:
            server["commands"] = [c for c in server["commands"] if c["name"] != cmd_name]
            save_config(self.data)
            self.build_tree()

    def add_global_command(self):
        dialog = CommandDialog(self)
        if dialog.exec():
            self.data["global_commands"].append(dialog.get_result())
            save_config(self.data)
            self.build_tree()

    def add_category_command(self, cat_item):
        dialog = CommandDialog(self)
        if dialog.exec():
            cat = cat_item.text(0)
            self.data["category_commands"].setdefault(cat, []).append(dialog.get_result())
            save_config(self.data)
            self.build_tree()

    def edit_category_command(self, cat_item):
        cat = cat_item.text(0)
        cmds = self.data["category_commands"].get(cat, [])
        names = [c["name"] for c in cmds]
        name, ok = QInputDialog.getItem(self, "Befehl wählen", "Befehl bearbeiten:", names, editable=False)
        if ok:
            cmd = next((c for c in cmds if c["name"] == name), None)
            if cmd:
                dialog = CommandDialog(self, command=cmd)
                if dialog.exec():
                    index = cmds.index(cmd)
                    self.data["category_commands"][cat][index] = dialog.get_result()
                    save_config(self.data)
                    self.build_tree()

    def delete_category_command(self, cat_item):
        cat = cat_item.text(0)
        cmds = self.data["category_commands"].get(cat, [])
        names = [c["name"] for c in cmds]
        name, ok = QInputDialog.getItem(self, "Befehl wählen", "Befehl löschen:", names, editable=False)
        if ok and QMessageBox.question(self, "Löschen", "Diesen Gruppenbefehl löschen?") == QMessageBox.StandardButton.Yes:
            self.data["category_commands"][cat] = [c for c in cmds if c["name"] != name]
            save_config(self.data)
            self.build_tree()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
