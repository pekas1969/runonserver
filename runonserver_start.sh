#!/bin/bash
# Starte das virtuelle Environment und die Anwendung

if [ ! -d "runonserver-env" ]; then
  echo "Virtuelles Environment 'runonserver-env' nicht gefunden. Bitte zuerst in der README.md das Environment anlegen."
  python3 -m venv runonserver-env
  #exit 1
fi

source runonserver-env/bin/activate
python3 run_on_server.py
deactivate
