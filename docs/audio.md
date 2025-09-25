# Audio

Documentation about the audio configuration the GUI app is built for.

## Audio Servers

The MultiFX GUI is built on [JACK (JACK Audio Connection Kit)](https://jackaudio.org/).
JACK is a professional, low-latency audio server for Linux. Using [Pipewire](https://www.pipewire.org/)
should also work just fine as it has support for JACK and other servers built
in.

Linux audio is weird due to the nature of the ecosystem being very modular and
customizable. If you run into an issue specific to your configuration, feel
free to open a GitHub issue.

Communication with the audio server occurs in `gui/src/modhostmanager.py`.
