import os
import subprocess
from config import OVPN_DIR

def get_activate_list() -> list:
    """
    取得目前正在執行中的 OpenVPN config 名稱清單（根據 process 列表）
    """
    configs = os.listdir("/run/openvpn")
    return configs



def parse_config(file_path: str) -> dict:
    """
    只擷取 OpenVPN config 的基本欄位（排除 <ca>、<key>、<cert> 等大型區塊）
    """
    config = {}
    skip_blocks = {"<ca>", "<cert>", "<key>", "<tls-auth>", "<extra-certs>"}
    current_block = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 開始跳過大型憑證區塊
            if any(line.lower().startswith(block) for block in skip_blocks):
                current_block = line.lower()
                continue
            if current_block and line.lower().startswith("</"):
                current_block = None
                continue
            if current_block:
                continue

            # 處理一般指令
            parts = line.split(None, 1)
            if len(parts) == 2:
                key, val = parts
                config[key] = val
            elif len(parts) == 1:
                config[parts[0]] = True  # 如 client, nobind 等
    if "auth-user-pass" in config:
        if config["auth-user-pass"] == True:
            config["auth"] = "require"
        else:
            config["auth"] = "correct" if check_auth(file_path) else "wrong"
    else:
        config["auth"] = "none"
    return config


def get_list() -> list:
    """
    回傳目前 OpenVPN 設定列表及其啟用狀態
    """
    file_list = [f for f in os.listdir(OVPN_DIR) if f.endswith(".ovpn")]
    activate_config = get_activate_list()
    config_info = []
    for f in file_list:
        config_info.append({
            "name": f,
            "type": "openvpn",
            "enabled": f in activate_config,
            "details": parse_config(f"{OVPN_DIR}/{f}")
        })
    return config_info

def auth(config:str,username:str,password:str):
    if config not in [f for f in os.listdir(OVPN_DIR) if f.endswith(".ovpn")]:
        return {"error":"config not found"}
    
    auth_file_path = f'{OVPN_DIR}/{config.replace(".ovpn",".key")}'
    with open (auth_file_path,"w") as f:
        f.writelines([username,"\n",password])
    
    with open(f"{OVPN_DIR}/{config}","r+") as f:
        data = f.read()
        if auth_file_path not in data:
            data = data.replace("auth-user-pass",f"auth-user-pass {auth_file_path}")
            f.write(data)


def enable(config: str, enable: bool) -> bool:
    """
    啟用或停用某個 OpenVPN config（使用 subprocess 控制 background process）
    """
    config_path = os.path.join(OVPN_DIR, config)

    if enable:
        # 啟用：以 background 模式啟動 OpenVPN，並將 stdout 導入 null
        status = subprocess.run(
            ["openvpn", "--config", config_path, "--daemon","--writepid",f"/run/ovpn/{config}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode
    else:
        pid_path = f"/run/ovpn/{config}"
        with open(pid_path,"r") as f:
            pid = f.read()
        status = subprocess.run(["kill",pid])
        os.remove(pid_path)
    return status == 0

def remove(config:str):
    key_path = OVPN_DIR + "/" +config.replace(".ovpn",".key")
    if os.path.isfile(key_path):
        os.remove(key_path)
    os.remove(f"{OVPN_DIR}/{config}")

def check_auth(config:str):
    ret = subprocess.run(["openvpn","--config",config],capture_output=True, text=True, timeout=3).stdout
    return  "AUTH_FAILED" not in ret