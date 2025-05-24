import sys
import os
import yaml
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QPushButton, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt

CONFIG_PATH = os.path.expanduser("~/.config/RunOnServer/servers.yaml")

class ServerEditor(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("RunOnServer - Server Editor")
        self.resize(800, 600)

        self.data = data
        self.servers = data.get("servers", [])
        self.category_commands = data.get("category_commands", {})
        self.global_commands = data.get("global_commands", [])

        # Aktuell ausgewählte Kategorie, Server, Kommando
        self.current_category = None
        self.current_server = None
        self.current_command = None
        self.current_global_command = None
        self.current_category_command = None

        # Layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Baumansicht
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Servers and Commands"])
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        main_layout.addWidget(self.tree)

        # Buttonbereiche für Server-Kommandos
        self.btn_layout_server = QHBoxLayout()
        self.btn_add_server_cmd = QPushButton("Add Server Command")
        self.btn_edit_server_cmd = QPushButton("Edit Server Command")
        self.btn_del_server_cmd = QPushButton("Delete Server Command")
        self.btn_add_server_cmd.clicked.connect(self.add_server_command)
        self.btn_edit_server_cmd.clicked.connect(self.edit_server_command)
        self.btn_del_server_cmd.clicked.connect(self.delete_server_command)
        self.btn_layout_server.addWidget(self.btn_add_server_cmd)
        self.btn_layout_server.addWidget(self.btn_edit_server_cmd)
        self.btn_layout_server.addWidget(self.btn_del_server_cmd)
        main_layout.addLayout(self.btn_layout_server)

        # Buttonbereiche für Kategorie-Kommandos
        self.btn_layout_category = QHBoxLayout()
        self.btn_add_cat_cmd = QPushButton("Add Category Command")
        self.btn_edit_cat_cmd = QPushButton("Edit Category Command")
        self.btn_del_cat_cmd = QPushButton("Delete Category Command")
        self.btn_add_cat_cmd.clicked.connect(self.add_category_command)
        self.btn_edit_cat_cmd.clicked.connect(self.edit_category_command)
        self.btn_del_cat_cmd.clicked.connect(self.delete_category_command)
        self.btn_layout_category.addWidget(self.btn_add_cat_cmd)
        self.btn_layout_category.addWidget(self.btn_edit_cat_cmd)
        self.btn_layout_category.addWidget(self.btn_del_cat_cmd)
        main_layout.addLayout(self.btn_layout_category)

        # Buttonbereiche für Globale Kommandos
        self.btn_layout_global = QHBoxLayout()
        self.btn_add_global_cmd = QPushButton("Add Global Command")
        self.btn_edit_global_cmd = QPushButton("Edit Global Command")
        self.btn_del_global_cmd = QPushButton("Delete Global Command")
        self.btn_add_global_cmd.clicked.connect(self.add_global_command)
        self.btn_edit_global_cmd.clicked.connect(self.edit_global_command)
        self.btn_del_global_cmd.clicked.connect(self.delete_global_command)
        self.btn_layout_global.addWidget(self.btn_add_global_cmd)
        self.btn_layout_global.addWidget(self.btn_edit_global_cmd)
        self.btn_layout_global.addWidget(self.btn_del_global_cmd)
        main_layout.addLayout(self.btn_layout_global)

        # Status Label
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        self.populate_tree()
        self.update_buttons_enabled(False)

    def populate_tree(self):
        self.tree.clear()

        # Kategorien aus Servern sammeln
        categories = {}
        for srv in self.servers:
            cat = srv.get("category", "Ungrouped")
            categories.setdefault(cat, []).append(srv)

        # Kategorien mit Servern und Kommandos
        for cat, servers in categories.items():
            cat_item = QTreeWidgetItem([cat])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, ("category", cat))
            self.tree.addTopLevelItem(cat_item)

            # Kategorie-Kommandos unter Kategorie
            cat_cmds = self.category_commands.get(cat, [])
            cat_cmds_item = QTreeWidgetItem(["Category Commands"])
            cat_cmds_item.setData(0, Qt.ItemDataRole.UserRole, ("category_commands", cat))
            cat_item.addChild(cat_cmds_item)
            for ccmd in cat_cmds:
                cmd_item = QTreeWidgetItem([ccmd["name"]])
                cmd_item.setData(0, Qt.ItemDataRole.UserRole, ("category_command", cat, ccmd))
                cat_cmds_item.addChild(cmd_item)

            # Server unter Kategorie
            for srv in servers:
                srv_item = QTreeWidgetItem([srv["name"]])
                srv_item.setData(0, Qt.ItemDataRole.UserRole, ("server", srv))
                cat_item.addChild(srv_item)

                # Server-Kommandos unter Server
                for cmd in srv.get("commands", []):
                    cmd_item = QTreeWidgetItem([cmd["name"]])
                    cmd_item.setData(0, Qt.ItemDataRole.UserRole, ("server_command", srv, cmd))
                    srv_item.addChild(cmd_item)

        # Globale Kommandos ganz unten
        global_root = QTreeWidgetItem(["Global Commands"])
        global_root.setData(0, Qt.ItemDataRole.UserRole, ("global_commands", None))
        self.tree.addTopLevelItem(global_root)
        for gcmd in self.global_commands:
            gcmd_item = QTreeWidgetItem([gcmd["name"]])
            gcmd_item.setData(0, Qt.ItemDataRole.UserRole, ("global_command", gcmd))
            global_root.addChild(gcmd_item)

        self.tree.expandAll()

    def on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            self.update_buttons_enabled(False)
            self.status_label.setText("")
            return

        kind = data[0]

        # Reset all current selections
        self.current_category = None
        self.current_server = None
        self.current_command = None
        self.current_global_command = None
        self.current_category_command = None

        if kind == "category":
            self.current_category = data[1]
            self.status_label.setText(f"Selected category: {self.current_category}")
            self.update_buttons_enabled(False)
        elif kind == "server":
            self.current_server = data[1]
            self.status_label.setText(f"Selected server: {self.current_server['name']}")
            self.update_buttons_enabled(False)
        elif kind == "server_command":
            self.current_server = data[1]
            self.current_command = data[2]
            self.status_label.setText(f"Selected server command: {self.current_command['name']}")
            self.update_buttons_enabled(True, for_type="server_command")
        elif kind == "category_commands":
            self.current_category = data[1]
            self.status_label.setText(f"Selected category commands for {self.current_category}")
            self.update_buttons_enabled(False)
        elif kind == "category_command":
            self.current_category = data[1]
            self.current_category_command = data[2]
            self.status_label.setText(f"Selected category command: {self.current_category_command['name']}")
            self.update_buttons_enabled(True, for_type="category_command")
        elif kind == "global_commands":
            self.status_label.setText("Selected global commands")
            self.update_buttons_enabled(False)
        elif kind == "global_command":
            self.current_global_command = data[1]
            self.status_label.setText(f"Selected global command: {self.current_global_command['name']}")
            self.update_buttons_enabled(True, for_type="global_command")
        else:
            self.update_buttons_enabled(False)
            self.status_label.setText("")

    def update_buttons_enabled(self, enabled, for_type=None):
        # Server command buttons
        self.btn_add_server_cmd.setEnabled(self.current_server is not None)
        self.btn_edit_server_cmd.setEnabled(enabled and for_type == "server_command")
        self.btn_del_server_cmd.setEnabled(enabled and for_type == "server_command")

        # Category command buttons
        self.btn_add_cat_cmd.setEnabled(self.current_category is not None)
        self.btn_edit_cat_cmd.setEnabled(enabled and for_type == "category_command")
        self.btn_del_cat_cmd.setEnabled(enabled and for_type == "category_command")

        # Global command buttons
        # Add is always enabled to add new global commands
        self.btn_add_global_cmd.setEnabled(True)
        self.btn_edit_global_cmd.setEnabled(enabled and for_type == "global_command")
        self.btn_del_global_cmd.setEnabled(enabled and for_type == "global_command")

    def add_server_command(self):
        if not self.current_server:
            self.show_error("Please select a server first.")
            return
        cmd = self.get_command_details()
        if cmd:
            self.current_server.setdefault("commands", []).append(cmd)
            self.save_data()
            self.populate_tree()

    def edit_server_command(self):
        if not self.current_command or not self.current_server:
            self.show_error("Please select a server command first.")
            return
        new_cmd = self.get_command_details(self.current_command)
        if new_cmd:
            # Update inplace
            self.current_command.update(new_cmd)
            self.save_data()
            self.populate_tree()

    def delete_server_command(self):
        if not self.current_command or not self.current_server:
            self.show_error("Please select a server command first.")
            return
        cmds = self.current_server.get("commands", [])
        cmds.remove(self.current_command)
        self.save_data()
        self.populate_tree()

    def add_category_command(self):
        if not self.current_category:
            self.show_error("Please select a category first.")
            return
        cmd = self.get_command_details()
        if cmd:
            self.category_commands.setdefault(self.current_category, []).append(cmd)
            self.save_data()
            self.populate_tree()

    def edit_category_command(self):
        if not self.current_category_command or not self.current_category:
            self.show_error("Please select a category command first.")
            return
        new_cmd = self.get_command_details(self.current_category_command)
        if new_cmd:
            self.current_category_command.update(new_cmd)
            self.save_data()
            self.populate_tree()

    def delete_category_command(self):
        if not self.current_category_command or not self.current_category:
            self.show_error("Please select a category command first.")
            return
        cmds = self.category_commands.get(self.current_category, [])
        cmds.remove(self.current_category_command)
        self.save_data()
        self.populate_tree()

    def add_global_command(self):
        cmd = self.get_command_details()
        if cmd:
            self.global_commands.append(cmd)
            self.save_data()
            self.populate_tree()

    def edit_global_command(self):
        if not self.current_global_command:
            self.show_error("Please select a global command first.")
            return
        new_cmd = self.get_command_details(self.current_global_command)
        if new_cmd:
            self.current_global_command.update(new_cmd)
            self.save_data()
            self.populate_tree()

    def delete_global_command(self):
        if not self.current_global_command:
            self.show_error("Please select a global command first.")
            return
        self.global_commands.remove(self.current_global_command)
        self.save_data()
        self.populate_tree()

    def get_command_details(self, cmd=None):
        """
        Öffnet Dialoge, um name, command und hold_terminal abzufragen.
        Falls cmd übergeben, werden Werte vorgefüllt (Editiermodus).
        Gibt dict oder None zurück.
        """
        name, ok = QInputDialog.getText(self, "Command Name", "Name:", QLineEdit.EchoMode.Normal, cmd["name"] if cmd else "")
        if not ok or not name.strip():
            return None
        command, ok = QInputDialog.getText(self, "Command", "Shell command:", QLineEdit.EchoMode.Normal, cmd["command"] if cmd else "")
        if not ok or not command.strip():
            return None
        hold_terminal, ok = QInputDialog.getItem(self, "Hold Terminal", "Hold terminal open after command?", ["True", "False"], 0 if (cmd and cmd.get("hold_terminal", True)) else 1, False)
        if not ok:
            return None
        return {
            "name": name.strip(),
            "command": command.strip(),
            "hold_terminal": hold_terminal == "True"
        }

    def show_error(self, msg):
        QMessageBox.warning(self, "Error", msg)

    def save_data(self):
        self.data["servers"] = self.servers
        self.data["category_commands"] = self.category_commands
        self.data["global_commands"] = self.global_commands

        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f, sort_keys=False)

def main():
    if not os.path.exists(CONFIG_PATH):
        # Erstelle default leere Struktur, falls nicht da
        data = {"servers": [], "category_commands": {}, "global_commands": []}
    else:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {"servers": [], "category_commands": {}, "global_commands": []}

    app = QApplication(sys.argv)
    editor = ServerEditor(data)
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
