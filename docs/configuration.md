# Configuration

Documentation for persistent configuration data pertaining.

## Config Hierarchy

### Profile

**Profiles** refer to the top-level pedalboard configuration, but not
configuration for the app.

Profiles contain the following:
- Name (generic like "profile 1" unless manually edited)
- List of plugins, ordered. Contains:
    - Plugin-id or name
    - Plugin preset name
    - Overwritten parameters for the preset including bypass

### Presets

**Presets** refer to the configuration of parameters for a single plug-in.

Presets contain the following:
- Name (again, generic like "preset 1" unless manually edited)
- Parameter name - value pairs.
