import os
import subprocess
from config import CLIENT_DIR,WG_DIR
from templates import INTERFACE,PEER
def get_list():
    return os.listdir(CLIENT_DIR)

def gen_server_config():
    private_key = os.popen(f"wg genkey").read()
    public_key = os.popen(f"echo {private_key}|wg pubkey").read()
    with open(f"{WG_DIR}/srv_master.conf","w") as f:
        f.write(INTERFACE.format(
            private_key=private_key,
        ))
    with open(f"{CLIENT_DIR}/server.pub","w") as f:
        f.write(public_key)
    
def write_client_config(name:str,client_private_key:str):
    with open(f"{CLIENT_DIR}/{name}.conf","w") as f:
        f.write(INTERFACE.format(
            private_key=client_private_key,
        ))
        with open(f"{CLIENT_DIR}/server.pub","r") as f2:
            server_public_key = f2.read()
        f.write(f"\n{PEER.format(public_key=server_public_key)}")

def write_server_peer(client_public_key:str):
    with open(f"{WG_DIR}/srv_master.conf","a") as f:
        f.write(f"\n{PEER.format(public_key=client_public_key)}")

def create(name):
    
    private_key = os.popen(f"wg genkey").read()
    public_key = os.popen(f"echo {private_key}|wg pubkey").read()
    write_client_config(name,private_key)
    if "srv_master.conf" not in os.listdir(CLIENT_DIR):
        gen_server_config()
    write_server_peer(name,private_key)
    return "ok"