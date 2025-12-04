import subprocess
import socket
import os
import time
import sys
import plugin_manager

PRINT_CMDS = False
MODHOST_PORT = 55555

SYSIN1 = "system:capture_1"
SYSIN2 = "system:capture_2"
SYSOUT1 = "system:playback_1"
SYSOUT2 = "system:playback_2"


def startModHost():
    # Starting mod-host -n(no ui) -p 5555(w/ port 5555)
    mod_host_cmd = ["mod-host", "-n", "-p", str(MODHOST_PORT)]
    try:
        subprocess.run(["killall", "mod-host"], check=False)

        if sys.platform.startswith("linux"):
            process = subprocess.Popen(
                    mod_host_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp
            )
        else:
            print("Unsupported OS")
            return None
        return process

    except Exception as e:
        print(f"Failed to start: {e}")
        return None


def startJackdServer():
    try:
        jackd_cmd = [
                "/usr/bin/jackd", "-d", "alsa", "-d", "hw:sndrpihifiberry",
                "-r", "96000", "-p", "128"
        ]

        if sys.platform.startswith("linux"):
            try:
                process = subprocess.Popen(
                    jackd_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    # Makes it independent of the parent process
                    preexec_fn=os.setpgrp,
                )
                # check to make sure that process doesn't error out
                time.sleep(2)  # give time to become stable

                # check for failure by seeing if process has ended or open failed
                jackd_failed: bool = process.poll() is not None
                if not jackd_failed and "Failed to open" in subprocess.communicate(timeout=2):
                    jackd_failed = True
                if jackd_failed:
                    # process ended
                    print("JACK server failed to start. Falling back to dummy.")
                    subprocess.run(["killall", "mod-host"], check=False)
                    jackd_cmd = [
                            "/usr/bin/jackd", "-d", "dummy", "-r", "96000",
                            "-p", "128"
                    ]
                    process = subprocess.Popen(
                        jackd_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        # Makes it independent of the parent process
                        preexec_fn=os.setpgrp,
                    )
                else:
                    print("JACK server started successfully.")
            except Exception as e:
                print(f"Error starting JACK server: {e}")
                return None
        else:
            print("Unsupported OS")
            return None

        return process

    except Exception as e:
        print(f"Failed to start: {e}")
        return None


def connectToModHost():
    HOST = "localhost"

    sock = None
    error_list: list[str] = []

    for _ in range(5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # Set the response timeout to 2 seconds
            sock.connect((HOST, MODHOST_PORT))
            print("Connected via socket")
            return sock
        except ConnectionRefusedError as e:
            error_list.append(f"Socket couldn't connect: {e}")
            time.sleep(1)

    print("Socket couldn't make a connection")
    for err in error_list:
        print(err)
    return None


def sendCommand(sock, command):
    if PRINT_CMDS:
        print(command)
    try:
        sock.sendall(command.encode()+b"\n")
        response = sock.recv(1024)
        return response.decode().replace('\x00', '')
    except socket.timeout:
        print(f"Socket timeout for command: {command}")
        return ""
    except Exception as e:
        print(f"Failed to send command: {e}")
        return None


def quitModHost(sock):
    command = "quit"
    try:
        return int(sendCommand(sock, command).split()[1])
    except Exception as e:
        print(e)
        return -5


def addEffect(sock, plugin: plugin_manager.Plugin, instanceNum: int):
    command = f"add {plugin.uri} {instanceNum}"
    try:
        return int(sendCommand(sock, command).split()[1])
    except Exception as e:
        print(f"Error addingEffect {e}")
        return -5


def connectMonoToMono(sock, source, dest):
    command = f"connect {source} {dest}"
    try:
        return int(sendCommand(sock, command).split()[1])
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5


def connectMonoToStereo(sock, source, dest_in_1, dest_in_2):
    command = f"connect {source} {dest_in_1}"
    try:
        response = sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5

    command = f"connect {source} {dest_in_2}"
    try:
        return [response, sendCommand(sock, command).split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5


def connectStereoToStereo(
        sock, source_out_1, source_out_2, dest_in_1, dest_in_2,
        flipped: bool = False
):
    res = ""
    if flipped:
        command = f"connect {source_out_1} {dest_in_2}"
        try:
            res = sendCommand(sock, command)
            response = res.split()[1]
        except Exception as e:
            print(f"Error connectingEffects {e}. Result: {res}")
            return -5
        command = f"connect {source_out_2} {dest_in_1}"
        try:
            res = sendCommand(sock, command)
            return [response, res.split()[1]]
        except Exception as e:
            print(f"Error connectingEffects {e}: Result: {res}")
            return -5
    else:
        command = f"connect {source_out_1} {dest_in_1}"
        try:
            res = sendCommand(sock, command)
            response = res.split()[1]
        except Exception as e:
            print(f"Error connectingEffects {e}. Result: {res}")
            return -5
        command = f"connect {source_out_2} {dest_in_2}"
        try:
            res = sendCommand(sock, command)
            return [response, res.split()[1]]
        except Exception as e:
            print(f"Error connectingEffects {e}: Result: {res}")
            return -5


def disconnectStereoToStereo(
        sock, source_out_1, source_out_2, dest_in_1, dest_in_2,
        flipped: bool = False
):
    res = ""
    if flipped:
        command = f"disconnect {source_out_1} {dest_in_2}"
        try:
            res = sendCommand(sock, command)
            response = res.split()[1]
        except Exception as e:
            print(f"Error disconnectingEffects {e}. Result: {res}")
            return -5
        command = f"disconnect {source_out_2} {dest_in_1}"
        try:
            res = sendCommand(sock, command)
            return [response, res.split()[1]]
        except Exception as e:
            print(f"Error connectingEffects {e}: Result: {res}")
            return -5
    else:
        command = f"disconnect {source_out_1} {dest_in_1}"
        try:
            res = sendCommand(sock, command)
            response = res.split()[1]
        except Exception as e:
            print(f"Error disconnectingEffects {e}. Result: {res}")
            return -5
        command = f"disconnect {source_out_2} {dest_in_2}"
        try:
            res = sendCommand(sock, command)
            return [response, res.split()[1]]
        except Exception as e:
            print(f"Error disconnectingEffects {e}: Result: {res}")
            return -5


def connectStereoToMono(sock, source_out_1, source_out_2, dest):
    command = f"connect {source_out_1} {dest}"
    try:
        response = sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5

    command = f"connect {source_out_2} {dest}"
    try:
        return [response, sendCommand(sock, command).split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5


def connectSystemCapturMono(sock, dest):
    command = f"connect system:capture_1 {dest}"
    res = ""
    try:
        res = sendCommand(sock, command)
        response = res.split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result: {res}")
        return -5

    command = f"connect system:capture_2 {dest}"
    try:
        res = sendCommand(sock, command)
        return [response, res.split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result: {res}")
        return -5


def connectSystemCapturStereo(sock, dest_in_1, dest_in_2):
    command = f"connect system:capture_1 {dest_in_1}"
    res = ""
    try:
        res = sendCommand(sock, command)
        response = res.split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result: {res}")
        return -5

    command = f"connect system:capture_2 {dest_in_2}"
    try:
        res = sendCommand(sock, command)
        return [response, res.split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result: {res}")
        return -5


def disconnectSystemCapturStereo(sock, dest_in_1, dest_in_2):
    command = f"disconnect system:capture_1 {dest_in_1}"
    res = ""
    try:
        res = sendCommand(sock, command)
        response = res.split()[1]
    except Exception as e:
        print(f"Error disconnectingEffects {e}. Result: {res}")
        return -5

    command = f"disconnect system:capture_2 {dest_in_2}"
    try:
        res = sendCommand(sock, command)
        return [response, res.split()[1]]
    except Exception as e:
        print(f"Error disconnectingEffects {e}. Result: {res}")
        return -5


def connectSystemPlaybackStereo(sock, source_out_1, source_out_2):
    command = f"connect {source_out_1} system:playback_1"
    res = ""
    try:
        res = sendCommand(sock, command)
        response = res.split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result {res}")
        return -5

    command = f"connect {source_out_2} system:playback_2"
    try:
        res = sendCommand(sock, command)
        return [response, res.split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result {res}")
        return -5


def disconnectSystemPlaybackStereo(sock, source_out_1, source_out_2):
    command = f"disconnect {source_out_1} system:playback_1"
    res = ""
    try:
        res = sendCommand(sock, command)
        response = res.split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result {res}")
        return -5

    command = f"disconnect {source_out_2} system:playback_2"
    try:
        res = sendCommand(sock, command)
        return [response, res.split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result {res}")
        return -5


def connectSystemPlaybackMono(sock, source):
    command = f"connnect {source} system:playback_1"
    res = ""
    try:
        res = sendCommand(sock, command)
        response = res.split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result: {res}")
        return -5

    command = f"connect {source} system:playback_2"
    res = sendCommand(sock, command)
    try:
        return [response, res.split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}. Result: {res}")
        return -5


def updateParameter(sock, instanceNum, parameter: plugin_manager.Parameter) -> int:
    if (parameter.type == "lv2"):
        command = f"param_set {instanceNum} {parameter.symbol} {parameter.value}"
        try:
            res = sendCommand(sock, command)
            return int(res.split()[1])
        except Exception as e:
            print(f"param_set error: {e}")
            return -5
    if (parameter.type == "plug"):
        command = f"patch_set {instanceNum} {parameter.symbol} {parameter.value}"
        try:
            res = sendCommand(sock, command)
            return int(res.split()[1])
        except Exception as e:
            print(f"patch_set error: {e}")
            return -5
    return -1


def updateBypass(sock, instanceNum, plugin: plugin_manager.Plugin):
    command = f"bypass {instanceNum} {plugin.bypass}"
    try:
        return sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error updatingBypass {e}")
        return -5


def setUpPlugins(sock, manager: plugin_manager.PluginManager):
    added = 0
    for instanceNum, plugin in enumerate(manager.plugins):
        response = addEffect(sock, plugin, instanceNum)
        if (response != instanceNum):
            print(instanceNum)
            print(response)
            print(f"Error adding plugins starting at: {plugin.name}.")
            if response == -101:
                print("mod-host responded -101: ERR_LV2_INVALID_URI. Is plugin installed?")
            return -5
        else:
            print(f"added {plugin.name}")
            added += 1
    return added


def setUpPatch(sock, manager: plugin_manager.PluginManager):
    prev = None
    for instanceNum, plugin in enumerate(manager.plugins):
        if instanceNum == 0:  # CONNECT INPUT TO FIRST PLUGIN
            if (plugin.channels == "mono"):
                connectSystemCapturMono(
                        sock,
                        f"effect_{instanceNum}:{plugin.inputs[0]}"
                )
            elif (plugin.channels == "stereo"):
                connectSystemCapturStereo(
                        sock,
                        f"effect_{instanceNum}:{plugin.inputs[0]}",
                        f"effect_{instanceNum}:{plugin.inputs[1]}"
                )
            else:
                print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                return -5
        if instanceNum == len(manager.plugins) - 1:  # CONNECT LAST PLUGIN TO OUT
            if (plugin.channels == "mono"):
                connectSystemPlaybackMono(sock, f"effect_{instanceNum}:{plugin.outputs[0]}")
            elif (plugin.channels == "stereo"):
                connectSystemPlaybackStereo(sock, f"effect_{instanceNum}:{plugin.outputs[0]}", f"effect_{instanceNum}:{plugin.outputs[1]}")
            else:
                print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                return -5
        if prev is not None:  # CONNECT ALL OTHER PLUGINS
            if (plugin.channels == "mono"):
                connectMonoToMono(
                    sock,
                    f"effect_{instanceNum-1}:{prev.outputs[0]}",
                    f"effect_{instanceNum}:{plugin.inputs[0]}"
                )
            elif (plugin.channels == "stereo"):
                connectStereoToStereo(
                    sock,
                    f"effect_{instanceNum-1}:{prev.outputs[0]}",
                    f"effect_{instanceNum-1}:{prev.outputs[1]}",
                    f"effect_{instanceNum}:{plugin.inputs[0]}",
                    f"effect_{instanceNum}:{plugin.inputs[1]}"
                )
            else:
                print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                return -5
        prev = plugin


def verifyParameters(sock, manager: plugin_manager.PluginManager):
    badParameters = []
    for instanceNum, plugin in enumerate(manager.plugins):
        for instanceNumP, parameter in enumerate(plugin.parameters):
            val = updateParameter(sock, instanceNum, parameter)
            if (val != 0):
                badParameters.append((plugin.name, parameter.name))
            time.sleep(.1)

    return badParameters


def tryCommand(sock, command, errMsg: str = ""):
    cmdout = ""
    try:
        cmdout = sendCommand(sock, command)
        return cmdout.split()[1]
    except Exception as e:
        print(f"MODHOST-COMMAND ERROR:\n\tEXCEPTION: {e}\n\tCOMMAND: {command} \n\tOUTPUT: {cmdout}\n\t{errMsg}")
        return -5


def patchThrough(sock):
    """Connects system in to system out"""
    tryCommand(sock, f"connect {SYSIN1} {SYSOUT1}")
    tryCommand(sock, f"connect {SYSIN2} {SYSOUT2}")


def unpatchThrough(sock):
    """Disconnects system in and system out"""
    tryCommand(sock, f"disconnect {SYSIN1} {SYSOUT1}")
    tryCommand(sock, f"disconnect {SYSIN2} {SYSOUT2}")


def remove(sock, instanceNum: int):
    """Helper function to remove plugins"""
    command = f"remove {instanceNum}"
    tryCommand(sock, command)


def removeFirst(sock, rmInstanceNum: int, rmPlugin: plugin_manager.Plugin,
                nextInstanceNum: int, nextPlugin: plugin_manager.Plugin):
    """Removes the first plugin. Note that the first instanceNum isn't always
    0 due to re-ordering and adding"""
    remove(sock, rmInstanceNum)
    connectSystemCapturStereo(
            sock,
            f"effect_{nextInstanceNum}:{nextPlugin.inputs[0]}",
            f"effect_{nextInstanceNum}:{nextPlugin.inputs[1]}"
    )


def removeMiddle(sock, rmInstanceNum: int, rmPlugin: plugin_manager.Plugin,
                 prevInstanceNum: int, prevPlugin: plugin_manager.Plugin,
                 nextInstanceNum: int, nextPlugin: plugin_manager.Plugin):
    """General use case for removing plugin. Not first or last plugin"""
    remove(sock, rmInstanceNum)
    connectStereoToStereo(
            sock,
            f"effect_{prevInstanceNum}:{prevPlugin.outputs[0]}",
            f"effect_{prevInstanceNum}:{prevPlugin.outputs[1]}",
            f"effect_{nextInstanceNum}:{nextPlugin.inputs[0]}",
            f"effect_{nextInstanceNum}:{nextPlugin.inputs[1]}"
    )


def removeLast(sock, rmInstanceNum: int, rmPlugin: plugin_manager.Plugin,
               prevInstanceNum: int, prevPlugin: plugin_manager.Plugin):
    """Removes the final plugin. Patches previous to system out."""
    remove(sock, rmInstanceNum)
    connectSystemPlaybackStereo(
            sock,
            f"effect_{prevInstanceNum}:{prevPlugin.outputs[0]}",
            f"effect_{prevInstanceNum}:{prevPlugin.outputs[1]}"
    )


def removeFinal(sock, instanceNum: int):
    """Removes final plugin. Patches system in to system out"""
    remove(sock, instanceNum)
    patchThrough(sock)


def add_plugin_end(sock, newInstanceNum: int, newPlugin: plugin_manager.Plugin,
                   lastInstanceNum: int, lastPlugin: plugin_manager.Plugin):
    """Adds a plugin at the end of the chain."""
    addEffect(sock, newPlugin, newInstanceNum)
    disconnectSystemPlaybackStereo(
            sock,
            f"effect_{lastInstanceNum}:{lastPlugin.outputs[0]}",
            f"effect_{lastInstanceNum}:{lastPlugin.outputs[1]}"
    )
    connectStereoToStereo(
            sock,
            f"effect_{lastInstanceNum}:{lastPlugin.outputs[0]}",
            f"effect_{lastInstanceNum}:{lastPlugin.outputs[1]}",
            f"effect_{newInstanceNum}:{newPlugin.inputs[0]}",
            f"effect_{newInstanceNum}:{newPlugin.inputs[1]}"
    )
    connectSystemPlaybackStereo(
            sock,
            f"effect_{newInstanceNum}:{newPlugin.outputs[0]}",
            f"effect_{newInstanceNum}:{newPlugin.outputs[1]}"
    )


def swap_plugins_start(sock, instanceNumA: int, pluginA: plugin_manager.Plugin,
                       instanceNumB: int, pluginB: plugin_manager.Plugin,
                       afterInstanceNum: int, afterPlugin: plugin_manager.Plugin):
    """Swaps the two plugins at the start of the chain.
    Start state: SYSIN -> pluginA -> pluginB -> afterPlugin
    End state: SYSIN -> pluginB -> pluginA -> afterPlugin
    """
    # disconnect all
    disconnectSystemCapturStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}",
    )
    disconnectStereoToStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}",
    )
    disconnectStereoToStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[0]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[1]}",
    )
    # reconnect
    connectSystemCapturStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}",
    )
    connectStereoToStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}",
    )
    connectStereoToStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[0]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[1]}",
    )


def swap_plugins_end(sock, instanceNumA: int, pluginA: plugin_manager.Plugin,
                     instanceNumB: int, pluginB: plugin_manager.Plugin,
                     beforeInstanceNum: int, beforePlugin: plugin_manager.Plugin):
    """Swaps the two plugins at the end of the chain
    Start state: beforePlugin -> pluginA -> pluginB -> SYSOUT
    End state: beforePlugin -> pluginB -> pluginA -> SYSOUT
    """
    # disconnect all
    disconnectStereoToStereo(
            sock,
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[0]}",
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[1]}",
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}"
    )
    disconnectStereoToStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}",
    )
    disconnectSystemPlaybackStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
    )
    # reconnect
    connectStereoToStereo(
            sock,
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[0]}",
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[1]}",
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}",
    )
    connectStereoToStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}",
    )
    connectSystemPlaybackStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
    )


def swap_plugins_middle(sock, instanceNumA: int, pluginA: plugin_manager.Plugin,
                        instanceNumB: int, pluginB: plugin_manager.Plugin,
                        beforeInstanceNum: int, beforePlugin: plugin_manager.Plugin,
                        afterInstanceNum: int, afterPlugin: plugin_manager.Plugin):
    """Swaps any two plugins not at the start or the end of the chain
    Start state: beforePlugin -> pluginA -> pluginB -> afterPlugin
    End state: beforePlugin -> pluginB -> pluginA -> afterPlugin
    """
    # disconnect all
    disconnectStereoToStereo(
            sock,
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[0]}",
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[1]}",
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}"
    )
    disconnectStereoToStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}",
    )
    disconnectStereoToStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[0]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[1]}",
    )
    # reconnect
    connectStereoToStereo(
            sock,
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[0]}",
            f"effect_{beforeInstanceNum}:{beforePlugin.outputs[1]}",
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}"
    )
    connectStereoToStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}",
    )
    connectStereoToStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[0]}",
            f"effect_{afterInstanceNum}:{afterPlugin.inputs[1]}",
    )


def swap_plugins_final(sock, instanceNumA: int, pluginA: plugin_manager.Plugin,
                       instanceNumB: int, pluginB: plugin_manager.Plugin):
    """Swaps the remaining two plugins in a chain
    Start state: SYSIN -> pluginA -> pluginB -> SYSOUT
    End state: SYSIN -> pluginB -> pluginA -> SYSOUT
    """
    # disconnect all
    disconnectSystemCapturStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}"
    )
    disconnectStereoToStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}",
    )
    disconnectSystemPlaybackStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
    )
    # reconnect
    connectSystemPlaybackStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.inputs[0]}",
            f"effect_{instanceNumB}:{pluginB.inputs[1]}"
    )
    connectStereoToStereo(
            sock,
            f"effect_{instanceNumB}:{pluginB.outputs[0]}",
            f"effect_{instanceNumB}:{pluginB.outputs[1]}",
            f"effect_{instanceNumA}:{pluginA.inputs[0]}",
            f"effect_{instanceNumA}:{pluginA.inputs[1]}",
    )
    connectSystemPlaybackStereo(
            sock,
            f"effect_{instanceNumA}:{pluginA.outputs[0]}",
            f"effect_{instanceNumA}:{pluginA.outputs[1]}",
    )
