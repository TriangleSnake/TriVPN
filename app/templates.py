from config import *

INTERFACE = f'''
[Interface]
PrivateKey = {{private_key}}
Address = {SRV_INT_IP}
ListenPort = {SRV_PUB_PORT}
'''

PEER = f'''
[Peer]
PublicKey = {{public_key}}
Endpoint = {SRV_PUB_IP}:{SRV_PUB_PORT}
AllowedIPs = {CLIENT_ALLOW_IP}
PersistentKeepalive = 25
'''