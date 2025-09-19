# MultiFX
This contains the code related to plugins, the GUI, and the MIDI footswitches
of the MultiFX Pedal project.

## Repo Outline (Proposed)

```
footswitch/ # Arduino code for the footswitch attachment
├ Footswitch_Code.ino # Arduino sketch. Move out of folder it's currently in.
| # We need to figure out what's going on with the .zip files.
gui/
| # We can probably ditch the old ASCII GUI stuff
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
  ├ gui/          # GUI arrangement and components
  └ audio/        # plugin host, JACK, socket stuff. We can rename this.
README.md
# We should also include the hardware schematics unless that's all done elsewhere.
```

## Run Locally

Below is a detailed guide on how to run the GUI locally for development.

### Dependencies

- Python
- PyQt5

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

**Show the commands needed to run the GUI here**

## Run on a Raspberry Pi

Below is a detailed guide on how to run the software on a Raspberry Pi

### Dependencies

- [Raspberry Pi OS](https://www.raspberrypi.com/software/)
- JACK
- Python
- PyQt5
