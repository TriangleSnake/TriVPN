import os
import subprocess
from config import WG_DIR
def get_activate_list()->list:
    activate_config = []
    data = os.popen("wg show").read()[1:].split("\n")
    for i in data:
        if i.startswith("interface"):
            config = i.split("\n")[0].removeprefix("interface: ")
            activate_config.append(config)
    return activate_config

def parse_config(name:str):
    data = subprocess.run(["wg-quick","strip",name.removesuffix(".conf")], capture_output=True, text=True).stdout[1:]
    data = data.split("\n\n")
    interface = data[0].splitlines()[1:]
    peer = data[1].splitlines()[1:]
    interface = dict([i.split(" = ") for i in interface])
    peer = dict([i.split(" = ") for i in peer])
    return {
        "Interface":interface,
        "Peer":peer
    }




def get_list()->dict:
    configs = []
    configs_name = [i for i in os.listdir(WG_DIR) if i.endswith(".conf")]
    activate_config = get_activate_list()
    for i in configs_name:
        config = {
            "name": i,
            "type": "wireguard",
            #"enabled": True,
            "enabled": i.removesuffix(".conf") in activate_config,
            "details": parse_config(i)
        }

        configs.append(config)
    return configs

def enable(config:str,enable:bool)->bool:
    command = "up" if enable else "down"
    status = subprocess.run(["wg-quick",command,config.removesuffix(".conf")]).returncode
    return status

def remove(config):
    os.remove(f"{WG_DIR}/{config}")