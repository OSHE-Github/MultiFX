import subprocess
import socket
import os
import time
import sys
import plugin_manager




def startModHost():
    try:
        mod_host_cmd = ["mod-host","-n","-p","5555"] #Starting mod-host -n(no ui) -p 5555(w/ port 5555)
        
        subprocess.run(["killall","mod-host"],check=False)

        if sys.platform.startswith("linux"):
            process = subprocess.Popen(mod_host_cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                         preexec_fn=os.setpgrp)
        else:
            print("Unsupported OS")
            return None
        return process
    
    except Exception as e:
        print(f"Failed to start: {e}")
        return None

def startJackdServer():
    try:
        jackd_cmd = ["/usr/bin/jackd", "-d", "alsa", "-d", "hw:sndrpihifiberry", "-r", "96000", "-p", "128", "-n", "2"]

        if sys.platform.startswith("linux"):
            try:
                process = subprocess.Popen(
                    jackd_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp,  # Makes it independent of the parent process
                )
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
    PORT = 5555

    sock = None

    for _ in range(5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(.5) #Set the response timeout to 2 seconds
            sock.connect((HOST, PORT))
            print("Connected via socket")
            return sock
        except ConnectionRefusedError:
            print("Socket couldnt connect...")
            time.sleep(1)
    
    print("Socket couldnt make a connection")
    return None

def sendCommand(sock, command):
    try:
        sock.sendall(command.encode()+b"\n")
        response = sock.recv(1024)
        return response.decode().replace('\x00', '')
    except socket.timeout:
        return ""
    except Exception as e:
        print(f"Failed to send command: {e}")
        return None

def quitModHost(sock):
    command = f"quit"
    try:
        return int(sendCommand(sock, command).split()[1])
    except Exception as e:
        print(e)
        return -5

def addEffect(sock, plugin: plugin_manager.Plugin, instanceNum : int):
    command = f"add {plugin.uri} {instanceNum}"
    try:
        return int(sendCommand(sock, command).split()[1])
    except Exception as e:
        print(f"Error addingEffect {e}")
        return -5

def connectMonoToMono(sock,source, dest):
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

def connectStereoToStereo(sock, source_out_1, source_out_2, dest_in_1, dest_in_2, flipped: bool = False):
    if flipped:
        command = f"connect {source_out_1} {dest_in_2}"
        try:
            response = sendCommand(sock, command).split()[1]
        except Exception as e:
            print(f"Error connectingEffects {e}")
            return -5
        command = f"connect {source_out_2} {dest_in_1}"
        try:
            return [response, sendCommand(sock, command).split()[1]]
        except Exception as e:
            print(f"Error connectingEffects {e}")
            return -5
    else:
        command = f"connect {source_out_1} {dest_in_1}"
        try:
            response = sendCommand(sock, command).split()[1]
        except Exception as e:
            print(f"Error connectingEffects {e}")
            return -5
        command = f"connect {source_out_2} {dest_in_2}"
        try:
            return [response, sendCommand(sock, command).split()[1]]
        except Exception as e:
            print(f"Error connectingEffects {e}")
            return -5

def connectStereoToMono(sock, source_out_1,source_out_2, dest):
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
    try:
        response = sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5
    
    command = f"connect system:capture_2 {dest}"
    try:
        return [response, sendCommand(sock, command).split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5

def connectSystemCapturStereo(sock, dest_in_1, dest_in_2):
    command = f"connect system:capture_1 {dest_in_1}"
    try:
        response = sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5
    
    command = f"connect system:capture_2 {dest_in_2}"
    try:
        return [response, sendCommand(sock, command).split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5

def connectSystemPlaybackStereo(sock, source_out_1, source_out_2):
    command = f"connect {source_out_1} system:playback_1"
    try:
        response = sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5
    
    command = f"connect {source_out_2} system:playback_2"
    try:
        return [response, sendCommand(sock, command).split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5

def connectSystemPlaybackMono(sock, source):
    command = f"connnect {source} system:playback_1"
    try:
        response = sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5
    
    command = f"connect {source} system:playback_2"
    try:
        return [response, sendCommand(sock, command).split()[1]]
    except Exception as e:
        print(f"Error connectingEffects {e}")
        return -5

def updateParameter(sock, instanceNum , parameter: plugin_manager.Parameter):
    if(parameter.type == "lv2"):
        command = f"param_set {instanceNum} {parameter.symbol} {parameter.value}"
        try:
            return sendCommand(sock, command).split()[1]
        except Exception as e:
            print(f"Error updatingParameter {e}")
            return -5
    if(parameter.type == "plug"):
        command = f"patch_set {instanceNum} {parameter.symbol} {parameter.value}"
        try:
            return sendCommand(sock, command).split()[1]
        except Exception as e:
            print(f"Error updatingParameter {e}")
            return -5

def updateBypass(sock, instanceNum, plugin: plugin_manager.Plugin):
    command = f"bypass {instanceNum} {plugin.bypass}"
    try:
        return sendCommand(sock, command).split()[1]
    except Exception as e:
        print(f"Error updatingBypass {e}")
        return -5

def setUpPlugins(sock, manager: plugin_manager.PluginManager):
    added=0
    for instanceNum, plugin in enumerate(manager.plugins):
        response = addEffect(sock, plugin, instanceNum)
        if(response != instanceNum):
            print(instanceNum)
            print(response)
            print(f"Invalid Plugin found {plugin.name}")
            print("invalid JSON")
            return -5
        else:
            print(f"added {plugin.name}")
            added =+1
    return added

def setUpPatch(sock, manager: plugin_manager.PluginManager):
    for instanceNum, plugin in enumerate(manager.plugins):
        if instanceNum == 0:
            if(plugin.channels == "mono"):
                connectSystemCapturMono(sock, f"effect_{instanceNum}:{plugin.inputs[0]}")
            elif(plugin.channels == "stereo"):
                connectSystemCapturStereo(sock, f"effect_{instanceNum}:{plugin.inputs[0]}", f"effect_{instanceNum}:{plugin.inputs[1]}")
            else:
                print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                return -5
        else:
            if(previous.channels == "mono"):
                if(plugin.channels == "mono"):
                    connectMonoToMono(sock, f"effect_{instanceNum-1}:{previous.outputs[0]}",
                                      f"effect_{instanceNum}:{plugin.inputs[0]}")
                elif(plugin.channels == "stereo"):
                    connectMonoToStereo(sock, f"effect_{instanceNum-1}:{previous.outputs[0]}",
                                        f"effect_{instanceNum}:{plugin.inputs[0]}",
                                        f"effect_{instanceNum}:{plugin.inputs[1]}")
                else:
                    print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                    return -5
            elif(previous.channels == "stereo"):
                if(plugin.channels == "mono"):
                    connectStereoToMono(sock, f"effect_{instanceNum-1}:{previous.outputs[0]}",
                                        f"effect_{instanceNum-1}:{previous.outputs[1]}",
                                        f"effect_{instanceNum}:{plugin.inputs[0]}" )
                elif(plugin.channels == "stereo"):
                    connectStereoToStereo(sock, f"effect_{instanceNum-1}:{previous.outputs[0]}",
                                        f"effect_{instanceNum-1}:{previous.outputs[1]}",
                                        f"effect_{instanceNum}:{plugin.inputs[0]}",
                                        f"effect_{instanceNum}:{plugin.inputs[1]}" )
                else:
                    print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                    return -5
            else:
                print(f"Error in plugin JSON {previous.name}. Invalid channel type: {previous.channels}")
                return -5
            if instanceNum == len(manager.plugins) - 1:
                if(plugin.channels == "mono"):
                    connectSystemPlaybackMono(sock, f"effect_{instanceNum}:{plugin.outputs[0]}")
                elif(plugin.channels == "stereo"):
                    connectSystemPlaybackStereo(sock, f"effect_{instanceNum}:{plugin.outputs[0]}", f"effect_{instanceNum}:{plugin.outputs[1]}")
                else:
                    print(f"Error in plugin JSON {plugin.name}. Invalid channel type: {plugin.channels}")
                    return -5
        previous = plugin

def varifyParameters(sock, manager: plugin_manager.PluginManager):
    badParameters = []
    for instanceNum, plugin in enumerate(manager.plugins):
        for instanceNumP, parameter in enumerate(plugin.parameters):
            val = updateParameter(sock, instanceNum, parameter)
            if(val != 0):
                badParameters.append((plugin.name,parameter.name))
            time.sleep(.1)
    
    return badParameters


