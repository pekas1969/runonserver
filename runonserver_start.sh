#!/bin/bash

# Aktiviert das virtuelle Environment
source runonserver-env/bin/activate

# Startet die Anwendung
python3 run_on_server.py

# Deaktiviert das virtuelle Environment nach Beenden der Anwendung
deactivate
