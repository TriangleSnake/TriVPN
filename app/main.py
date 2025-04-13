from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import re
import wireguard, openvpn, clients
from config import *
app = FastAPI()

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    name: str
    username: str
    password: str

class ConfigToggle(BaseModel):
    name: str
    type: str
    enabled: bool


class ConfigDelete(BaseModel):
    name: str
    type: str

def sanitize_filename(filename: str) -> str:
    basename = os.path.basename(filename)  # 移除路徑，例如 ../a.conf -> a.conf
    name_only = basename.rsplit(".", 1)[0]  # 移除副檔名

    pattern = re.compile(r'^[a-zA-Z0-9_]+$')  # 加入數字支援
    if not pattern.fullmatch(name_only):
        raise HTTPException(status_code=400, detail="Filename can only contain letters, numbers and underscores (a-zA-Z0-9_)")
    

def check_config_type(type):
    if type not in CONFIG_TYPE:
        raise HTTPException(status_code=400, detail="Invalid type")

@app.post("/api/config/upload")
async def upload_config(file: UploadFile = File(...), type: str = Form(...)):
    check_config_type(type)
    path = WG_DIR if type == "wireguard" else OVPN_DIR
    
    

    sanitize_filename(file.filename)
    
    path = os.path.join(path, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Uploaded successfully"}


@app.get("/api/config/list")
async def list_configs(type: str):
    check_config_type(type)
    if type == "wireguard":
        return wireguard.get_list()
    else:
        return openvpn.get_list()


@app.post("/api/config/enable")
async def enable_config(data: ConfigToggle):
    name = data.name
    type = data.type
    enable = data.enabled
    check_config_type(type)
    if type == "wireguard":
        status = wireguard.enable(name,enable)
    else:
        status = openvpn.enable(name,enable)
    if status == 0:
        return {enable:"success"}
    else:
        return {enable:"fail"}

@app.post("/api/config/auth")
async def add_auth(data: AuthRequest):
    name = data.name
    username = data.username
    password = data.password
    sanitize_filename(name)
    openvpn.auth(name,username,password)

@app.delete("/api/config")
async def delete_config(data: ConfigDelete):
    name = data.name
    type = data.type
    sanitize_filename(name)
    check_config_type(type)
    if type == "wireguard":
        wireguard.remove(name)
    else:
        openvpn.remove(name)
    return {"message": "Deleted"}


@app.get("/api/client/list")
async def list_clients():
    return clients.get_list()


@app.post("/api/client")
async def create_client(name: str = Form(None)):
    clients.create_client(name)


@app.get("/api/client/config/{name}")
async def download_client(name: str):
    path = os.path.join(CLIENT_DIR, f"{name}.conf")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Client not found")
    return FileResponse(path, media_type='text/plain', filename=f"{name}.conf")


@app.delete("/api/client/{name}")
async def delete_client(name: str):
    global clients
    clients = [c for c in clients if c["name"] != name]
    path = os.path.join(CLIENT_DIR, f"{name}.conf")
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return {"message": "Deleted"}

@app.get("/",response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()