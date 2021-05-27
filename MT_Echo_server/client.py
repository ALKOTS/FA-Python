import socket
import logging
from threading import Thread
import sys
import pickle
from validation import ip_validation, port_validation
from getpass import getpass
from time import sleep

IP_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 9090
logging.basicConfig(filename='Logs/client.log',
                    format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s", level=logging.INFO)

server_ip=""
port=0
status=""

sock=""
username=""
data=""

statuses={}


def server_connection():
    global server_ip, port, status, sock, username, data
    sock = socket.socket()
    sock.setblocking(1)
    try:
        sock.connect((server_ip, port))
    except ConnectionRefusedError:
        print(f"Unable to connect {server_ip, port}")
        sys.exit(0)
    
    logging.info(
        f"Established connection {sock.getsockname()} with ('{server_ip}', {port})")

def polling():
    global server_ip, port, status, sock, username, data, statuses
    Thread(target=recv).start()
    print("Use 'exit', to disconnect")
    while status != 'finish':
        try:
            statuses[status]()
        except KeyError:
            msg = input(f"{username}> ")
            if msg != "":
                if msg == "exit":
                    status = "finish"
                    logging.info(f"Disconnecting {sock.getsockname()} from server")
                    break
                sendM = pickle.dumps(["message", msg, username])
                sock.send(sendM)
                logging.info(f"Sending data from {sock.getsockname()}: {msg}")
    sock.close()

def sendPasswd():
    global server_ip, port, status, sock, username, data
    passwd = getpass(data)
    sock.send(pickle.dumps(["passwd", passwd]))
    sleep(1.5)

def auth():
    global server_ip, port, status, sock, username, data
    print("Введите имя:")
    username = input()
    sock.send(pickle.dumps(["auth", username]))
    sleep(1.5)
    logging.info(f"{sock.getsockname()} registered")

def success():
    global server_ip, port, status, sock, username, data
    print(data)
    status = "ready"
    username = data.split(" ")[1]
    logging.info(f"Client {sock.getsockname()} authorized")

def recv():
    global server_ip, port, status, sock, username, data
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                sys.exit(0)
            status = pickle.loads(data)[0]
            if status == "message":
                print(f"\n{pickle.loads(data)[2]} -->", pickle.loads(data)[1])
                logging.info(f"Client {sock.getsockname()} recieved data: {pickle.loads(data)[1]}")
            else:
                data = pickle.loads(data)[1]
                
        except OSError:
            break


statuses={
	"auth":auth,
	"passwd":sendPasswd,
	"success":success
}

user_port = input("Enter port (enter for default):")
if not port_validation(user_port):
	user_port = PORT_DEFAULT
	print(f"Set {user_port} as default port")

user_ip = input("Enter user ip (enter for default):")
if not ip_validation(user_ip):
	user_ip = IP_DEFAULT
	print(f"Set {user_ip} as default")

server_ip=user_ip
port=int(user_port)
server_connection()
polling()

