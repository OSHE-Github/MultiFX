import json
import os

from utils import profiles_dir


class Parameter():
    def __init__(self, type: str, name: str, symbol: str, mode: str,
                 value: float, min: float, max: float):
        self.type = type
        self.name = name
        self.symbol = symbol
        self.mode = mode
        self.value = value
        self.minimum = min
        self.max = max
        match self.mode:
            case "dial":
                self.increment = (max - min)/100
            case "button" | "selector":
                self.increment = 1

    def setValue(self, value: float):
        self.value = value


class Plugin():
    def __init__(self, name: str, uri: str, channels: str, inputs: list,
                 outputs: list, bypass: float = 0, paramters: list = None):
        self.name = name
        self.uri = uri
        self.bypass = bypass
        self.channels = channels
        self.inputs = inputs
        self.outputs = outputs
        # initalize parameters if there are any otherwise initalize an empty list
        self.parameters = paramters if paramters else []

    def add_parameter(self, parameter: Parameter):
        self.parameters.append(parameter)


class PluginManager:
    def __init__(self, plugins: list = None):
        self.plugins = plugins if plugins else []

    def getPluginNames(self):
        names = []
        for plugin in self.plugins:
            names.append(plugin.name)
        return names

    def getParameterNames(self, x: int):
        try:
            names = []
            for parameter in self.plugins[x].parameters:
                names.append(parameter.name)

            return names
        except Exception as e:
            print(e)
            return []

    def size(self):
        return len(self.plugins)

    def paramSize(self, x: int):
        return len(self.plugins[x].parameters)

    def getPlugin(self, x: int):
        try:
            return self.plugins[x]
        except IndexError:
            print("Index does not exist")
            return []

    def addPlugin(self, plugin: Plugin):
        self.plugins.append(plugin)

    @staticmethod
    def clone_plugin(plugin: Plugin) -> Plugin:
        parameters = []
        for param in plugin.parameters:
            parameters.append(Parameter(
                type=param.type,
                name=param.name,
                symbol=param.symbol,
                mode=param.mode,
                value=param.value,
                min=param.minimum,
                max=param.max,
            ))

        return Plugin(
            name=plugin.name,
            uri=plugin.uri,
            bypass=plugin.bypass,
            channels=plugin.channels,
            inputs=list(plugin.inputs),
            outputs=list(plugin.outputs),
            paramters=parameters,
        )

    def changeParameter(self, pluginIndex: int, parameterIndex: int,
                        value: float):
        try:
            plugin = self.plugins[pluginIndex]
            try:
                parameter = plugin.parameters[parameterIndex]
                parameter.setValue(value)

            except IndexError:
                print("Parameter index does not exist")
                return None

        except IndexError:
            print("Plugin index does not exist")
            return None

    def all_plugins():
        json_path = os.path.join(profiles_dir, "all_plugins.json")
        mgr = PluginManager()
        mgr.initFromJSON(json_path)
        return mgr.plugins

    def initFromJSON(self, jsonFile: str):
        try:
            with open(jsonFile, "r") as file:
                data = json.load(file)
                if "plugins" not in data:
                    raise ValueError("Missing 'plugins' field")

                for plugin_data in data["plugins"]:
                    name = plugin_data.get("name", "plugin")
                    if "uri" not in plugin_data:
                        raise ValueError("No uri included")
                    uri = plugin_data.get("uri")
                    bypass = plugin_data.get("bypass", 0)
                    channels = plugin_data.get("channels", "mono")
                    inputs = plugin_data.get("inputs", ["in"])
                    outputs = plugin_data.get("outputs", ["out"])

                    parameters = []

                    for param_data in plugin_data.get("parameters", []):
                        try:
                            parameter = Parameter(
                                type=param_data.get("type", "lv2"),
                                name=param_data.get("name", "parameter"),
                                symbol=param_data["symbol"],
                                mode=param_data.get("mode", "dial"),
                                min=param_data["min"],
                                max=param_data["max"],
                                value=param_data.get("value",
                                                    param_data.get("default",
                                                                   1.0))
                            )
                            parameters.append(parameter)
                        except KeyError as e:
                            print(f"Skipping parameter {name} due to missing key: {e}")
                    self.addPlugin(Plugin(
                            name=name,
                            uri=uri,
                            bypass=bypass,
                            channels=channels,
                            inputs=inputs,
                            outputs=outputs,
                            paramters=parameters
                        ))

        except json.JSONDecodeError:
            print("Invalid JSON format!")
            return -1
        except FileNotFoundError:
            print("Invalid path to JSON")
            return -1
        except ValueError as e:
            print(f"JSON Error: {e}")

    def serialize(self):
        """Return the current plugin configuration as a dict."""
        plugin_data = []
        for plugin in self.plugins:
            params = []
            for param in plugin.parameters:
                params.append({
                    "type": param.type,
                    "name": param.name,
                    "symbol": param.symbol,
                    "mode": param.mode,
                    "min": param.minimum,
                    "max": param.max,
                    "value": param.value,
                    "default": param.value,
                })

            plugin_data.append({
                "name": plugin.name,
                "uri": plugin.uri,
                "bypass": plugin.bypass,
                "channels": plugin.channels,
                "inputs": plugin.inputs,
                "outputs": plugin.outputs,
                "parameters": params,
            })

        return {"plugins": plugin_data}

    def save_to_profile(self, profile_name: str) -> str:
        """Save the current plugin state to a profile file.

        Args:
            profile_name: Name of the profile without the extension.

        Returns:
            Path to the saved profile file.
        """
        if not profile_name:
            raise ValueError("Profile name is required to save the board")

        profile_path = os.path.join(profiles_dir, f"{profile_name}.json")
        with open(profile_path, "w") as file:
            json.dump(self.serialize(), file, indent=4)

        return profile_path
