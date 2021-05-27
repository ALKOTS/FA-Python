import socket
from datetime import datetime
import hashlib
import json
import pickle
from threading import Thread
import sys
import logging
from validation import is_free_port, port_validation


PORT_DEFAULT = 9090
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s", handlers=[logging.FileHandler("Logs/server.log"), logging.StreamHandler()], level=logging.INFO)

users="users.json"
clients=[]
server_port=None
all_Users=[]
status=None


def readJSON():
    global users, clients, server_port, all_Users, status
    with open(users, 'r') as f:
        users_dict = json.load(f)
        
    return users_dict

def writeJSON():
    global users, clients, server_port, all_Users, status
    with open(users, 'w') as f:
        json.dump(all_Users, f, indent=4)

def server_boot():
    global users, clients, server_port, all_Users, status

    sock = socket.socket()
    sock.bind(('', server_port))
    sock.listen(5)
    sock = sock
    logging.info(f"Server started, port: {server_port}")
    while True:
        conn, addr = sock.accept()
        Thread(target=listenToClient, args=(conn, addr)).start()
        logging.info(f"Client: {addr}")
        clients.append(conn)

def broadcast(msg, conn, address, username):
    global users, clients, server_port, all_Users, status

    username += "_"+str(address[1])
    for sock in clients:
        if sock != conn:
            data = pickle.dumps(["message", msg, username])
            sock.send(data)
            logging.info(f"Sending to {sock.getsockname()}: {msg}")
        

def checkPassword(passwd, userkey):
    global users, clients, server_port, all_Users, status

    key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
    return key == userkey

def generateHash(passwd):
    global users, clients, server_port, all_Users, status

    key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
    return key

def listenToClient(conn, address):
    global users, clients, server_port, all_Users, status

    authorization(address, conn)
    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            conn.close()
            clients.remove(conn)
            logging.info(f"Disconnecting {address}")
            break

        if data:
            status, data, username = pickle.loads(data)
            logging.info(f"Recieving from '{username}_{address[1]}': {data}")
            if status == "message":
                broadcast(data, conn, address, username)
                
        else:
            conn.close()
            clients.remove(conn)
            logging.info(f"Disconnecting {address}")
            break

def authorization(addr, conn):
    global users, clients, server_port, all_Users, status
    print(type(users))
    try:
        all_Users = readJSON()
    except json.decoder.JSONDecodeError:
        registration(addr, conn)

    user_flag = False
    for user in all_Users:
        if addr[0] in user:
            for k, v in user.items():
                if k == addr[0]:
                    name = v['name']
                    password = v['password']
                    conn.send(pickle.dumps(["passwd", "Enter your password: "]))
                    passwd = pickle.loads(conn.recv(1024))[1]
                    conn.send(pickle.dumps(["success", f"Hello, {name}"])) if checkPassword(
                        passwd, password) else authorization(addr, conn)
                    user_flag = True
    if not user_flag:
        registration(addr, conn)
        

    def registration(addr, conn):
        global users, clients, server_port, all_Users, status

        conn.send(pickle.dumps(
            ["auth", ""]))
        name = pickle.loads(conn.recv(1024))[1]
        conn.send(pickle.dumps(["passwd", "Enter password: "]))
        passwd = generateHash(pickle.loads(conn.recv(1024))[1])
        conn.send(pickle.dumps(["success", f"Hello {name}"]))
        all_Users.append({addr[0]: {'name': name, 'password': passwd}})
        writeJSON()
        all_Users = readJSON()



server_port = PORT_DEFAULT
if not port_validation(PORT_DEFAULT, True):
    if not is_free_port(PORT_DEFAULT):
        logging.info(f"Default port {PORT_DEFAULT} already taken")
        free_port = False
        while not free_port:
            server_port += 1
            free_port = is_free_port(server_port)
try:
    server_boot()
except KeyboardInterrupt:
    logging.info(f"Stopping server")


