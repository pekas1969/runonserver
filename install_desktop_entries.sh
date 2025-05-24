#!/bin/bash

# Absoluter Pfad zum Projektverzeichnis (automatisch bestimmt)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Zielverzeichnis für Desktop-Dateien (nur für aktuellen User)
DESKTOP_DIR="$HOME/.local/share/applications"

# Erstelle Zielverzeichnis, falls nicht vorhanden
mkdir -p "$DESKTOP_DIR"

# Desktop-Datei für RunOnServer
cat > "$DESKTOP_DIR/runonserver.desktop" <<EOF
[Desktop Entry]
Name=RunOnServer
Comment=Startet das RunOnServer Tray-Icon zur Serversteuerung
Exec=python3 $PROJECT_DIR/run_on_server.py
Icon=network-server
Terminal=false
Type=Application
Categories=Network;
EOF

# Desktop-Datei für RunOnServer Editor
cat > "$DESKTOP_DIR/runonserver-editor.desktop" <<EOF
[Desktop Entry]
Name=RunOnServer Editor
Comment=Bearbeitet die Serverkonfiguration
Exec=python3 $PROJECT_DIR/server_editor.py
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Network;
EOF

# Berechtigungen setzen
chmod +x "$DESKTOP_DIR"/runonserver*.desktop

# Menü-Datenbank aktualisieren (optional, für sofortiges Anzeigen)
update-desktop-database "$DESKTOP_DIR" 2>/dev/null

echo "Desktop-Verknüpfungen wurden erstellt:"
echo "  - RunOnServer"
echo "  - Server Editor"
echo "Sie sollten nun im Anwendungsmenü unter 'Internet' erscheinen."
