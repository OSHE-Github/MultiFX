# Offboard Configuration

At start, the MultiFX GUI will scan for USB drives that contain configuration
data by matching a directory with `/dev/sd*/multifx`. In Linux, all USB drives
will match `/dev/sd*`, so on the user end, you must plug in a USB with the
folder `multifx` in the root directory.

For simplicity, everything in that directory will be copied to the app's config
directory on startup whenever possible with `try_load()` in `offboard.py`.
Similarly, we will write all data from the config directory to the USB whenever 
a write occurs using `try_save()`. This can be optimized in the future.
