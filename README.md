# MultiFX
This contains the code related to plugins, the GUI, and the MIDI footswitches
of the MultiFX Pedal project.

## Repo Outline 

```
docs/       # Documentation for specific features
footswitch/ # Arduino code for the footswitch attachment
├ Footswitch_Code.ino # Arduino sketch. 
└ *.zip     # I think this is EE type stuff, someone else describe this. -Jay
gui/
├ assets/         # Images and such
├ config/         # This can be backed up to USB or be located elsewhere later.
| ├ profile.json  # High level config
| └ plugins/      # Plugin configurations (not binaries)
|   └ <plugin>/   # (placeholder) name after plugin
|     ├ <plugin>.json   # Configures plugin params and order of presets
|     └ presets/
|       └ <preset>.json
└ src/            # Python code
  ├ main.py       # Run this file
  └ qwidgets/     # GUI components
README.md         # General overview
# We should also include the hardware schematics unless that's all done elsewhere.
```

## Run Locally

Below is a detailed guide on how to run the GUI locally for development.

### Dependencies

- Python
- PyQt5
- [KodeMono](https://kodemono.com/) font

Commands to install dependencies may vary on system. Try pip first.

```
pip install PyQt5
```

If you get an error about an "externally managed environment", try using your
system's package manager:

```
sudo pacman -S python-pyqt5
```

### Running the GUI

Running the GUI is very simple.

Navigate to the src directory.

```bash
cd gui/src
```

Run `main.py`

```bash
python main.py
```

Running locally may yield some bugs depending on the audio configuration of
your system. Errors will be printed when the system appears to be
misconfigured, but the GUI should still work for testing navigation and
visuals.

## Run on a Raspberry Pi

Below is a detailed guide on how to run the software on a Raspberry Pi

### Dependencies

- [Raspberry Pi OS](https://www.raspberrypi.com/software/)
- JACK
- Python
- PyQt5
