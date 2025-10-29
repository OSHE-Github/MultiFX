# Offboard Configuration

At start, the MultiFX GUI will scan for USB drives that contain configuration
data by matching a directory with `/run/media/{username}/{device}/multifx`.
This should support any type of external drive, but was only tested on USB
drives. Some distros might map to a different location. Depending on your
system, you may need to change the value of `USB_DIR` in `offboard.py`.

For simplicity, everything in that directory will be copied to the app's config
directory on startup whenever possible with `try_load()` in `offboard.py`.
Similarly, we will write all data from the config directory to the USB whenever 
a write occurs using `try_save()`. This can be optimized in the future.
