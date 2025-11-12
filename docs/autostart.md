# Auto-Starting GUI

To start the GUI automatically on a Raspberry Pi, create a `.desktop` with the
following contents:

```
[Desktop Entry]
Type=Application
Name=MyGUI
Exex= bash -c "sleep 1 && python3 <path to main.py>"
StartupNotify=false
```
