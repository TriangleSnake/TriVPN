from config import *
import sqlite3
import os

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 建立 clients table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        private_key TEXT NOT NULL,
        public_key TEXT NOT NULL,
        config_name TEXT NOT NULL,
        config_body TEXT NOT NULL,
        filename TEXT NOT NULL,
        ip TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )''')

    # 建立 server_info table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS server (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        private_key TEXT NOT NULL,
        public_key TEXT NOT NULL
    )''')
    
    private_key = os.popen("wg genkey").read().strip()
    public_key = os.popen(f"echo {private_key} | wg pubkey").read().strip()
    cur.execute('''
                INSERT INTO server (private_key, public_key) VALUES (?, ?)
                ''', (private_key, public_key))

    conn.commit()
    conn.close()

if not os.path.exists(DB_PATH):
    init_db()

def get_list() -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients')
    rows = cur.fetchall()
    conn.close()
    clients = []
    for row in rows:
        client = {
            "id": row[0],
            "private_key": row[1],
            "public_key": row[2],
            "config_name": row[3],
            "config_body": row[4],
            "filename": row[5],
            "ip": row[6],
            "created_at": row[7]
        }
        clients.append(client)
    return clients


def get_ip():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT ip FROM clients")
        used_ips = {row[0] for row in cur.fetchall()}
        base_ip = "10.0.0."
        for i in range(2, 255):  # 從 10.0.0.2 ~ 10.0.0.254
            ip = base_ip + str(i)
            if ip not in used_ips:
                return ip
        raise Exception("No available IPs")


def create(name: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    client_private_key = os.popen("wg genkey").read().strip()
    client_public_key = os.popen(f"echo {client_private_key} | wg pubkey").read().strip()
    server_public_key = cur.execute('SELECT public_key FROM server').fetchone()[0]
    ip = get_ip()

    config_body = f"""
[Interface]
PrivateKey = {client_private_key}
Address = {ip}/32
DNS = 1.1.1.1

[Peer]
PublicKey = {server_public_key}
Endpoint = {SRV_PUB_IP}:{SRV_PUB_PORT}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    
    config_name = name
    filename = f"client_{name}.conf"
    cur.execute('''
                INSERT INTO clients (private_key, public_key, config_name, config_body, filename, ip) VALUES (?, ?, ?, ?, ?)
                ''', (client_private_key, client_public_key, config_name, config_body, filename, ip))
    conn.commit()
    conn.close()
    return {"message": "Client created"}