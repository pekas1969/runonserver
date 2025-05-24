# RunOnServer

RunOnServer is a lightweight system tray tool to execute commands on remote servers via SSH. It supports organizing servers by categories, sending commands to individual or multiple servers, and defining reusable global and group-specific commands.

---

## 🛠 Installation

```bash
git clone https://github.com/pekas1969/RunOnServer.git
cd RunOnServer
python3 -m venv runonserver-env
source runonserver-env/bin/activate
pip install -r requirements.txt
```

## 🚀 Starten

```bash
./runonserver_start.sh
```

## 🗂 Konfiguration (`~/.config/RunOnServer/servers.yaml`)

```yaml
servers:
  - name: "Webserver"
    host: "192.168.177.5"
    user: "root"
    category: "Servers-Home"
    commands:
      - name: "Apache neu starten"
        command: "sudo systemctl restart apache2"
        hold_terminal: true

category_commands:
  "Servers-Home":
    - name: "Alle Webserver neustarten"
      command: "sudo reboot"
      hold_terminal: false

global_commands:
  - name: "System aktualisieren"
    command: "sudo apt update && sudo apt upgrade -y"
    hold_terminal: true
```

---

## 🧽 Deinstallation

```bash
rm -rf ~/.config/RunOnServer
rm -rf runonserver-env
```

---

## 📬 Contact

Peter Kasparak  
📧 peter.kasparak@gmail.com
