from config import *

SRV_INTERFACE = f'''
[Interface]
PrivateKey = {{server_private_key}}
Address = {SRV_INT_IP}
ListenPort = {SRV_PUB_PORT}
'''

SRV_PEER = f'''
[Peer]
PublicKey = {{client_public_key}}
Endpoint = {SRV_PUB_IP}:{SRV_PUB_PORT}
AllowedIPs = {CLIENT_ALLOW_IP}
PersistentKeepalive = 25
'''