# MultiFX

Code and documentation for the open-source Raspberry Pi-based audio-effects 
pedal.

**IMPORTANT!**

If audio ever stops coming through from your profile, go back to the profile
selection page and re-enter the profile until it works. We were unfortunately
unable to find the root cause of this before the deadline due to its random
nature.

## Outline 

```
docs/                           # Documentation for specific features
footswitch/                     # Arduino code for the footswitch attachment
├ Footswitch_Code.ino           # Arduino sketch. 
└ *.zip                         
gui/
├ assets/                       # Images for GUI visuals
├ config/                       # User configuration. Profiles, plugins, presets.
| ├ profile.json                # Overall pedalboard config
| └ plugins/                    # Plugin configurations (not binaries)
|   └ <plugin>/                 # (placeholder) name after plugin
|     ├ <plugin>.json           # Configures plugin params and order of presets
|     └ presets/                # Presets for plugin parameters
|       └ <preset>.json
└ src/                          # Python code
  ├ main.py                     # This file starts up the program
  ├ styles.py                   # Variables/constants for visuals. Colors, fonts, proportions, etc. 
  └ qwidgets/                   # GUI components
README.md                       # General overview
```

## Run Locally

Below is a detailed guide on how to run the GUI locally for development.

### Dependencies

- Python
- PyQt5
- PyFilesystem (fs)
- [KodeMono](https://kodemono.com/) Recommended font for GUI. If you want to 
  have your own, you must change the `font_family` variable in 
  `gui/src/styles.py`.
- [mod-host](https://github.com/mod-audio/mod-host)

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
your system. Check command-line output if unexpected audio/GUI behavior is
occuring.

Below is a minimal example of how to start up `jackd` and `mod-host` to be
able to navigate the GUI.

```
jackd -d dummy
```

```
mod-host
```
