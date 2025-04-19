# Configuration path for WireGuard and OpenVPN
WG_DIR = "/etc/wireguard"
OVPN_DIR = "/etc/openvpn/config"
CLIENT_DIR = "/etc/clients"
CONFIG_TYPE = ["wireguard","openvpn"]

#IP setting
SRV_INT_IP = "10.11.12.1/24"
SRV_PUB_IP = "1.2.3.4"
SRV_PUB_PORT = 51820
CLIENT_ALLOW_IP = "10.0.0.0/8,192.168.22.0/24"