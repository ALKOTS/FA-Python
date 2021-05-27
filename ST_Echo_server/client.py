import socket

class MyExit(Exception):
    pass

sock = socket.socket()
server = input("Enter server IP:")
port = input("Enter server port:")

if server == '':
    server = '127.0.0.1'
if port == '':
    port = 9090

try:
    sock.connect((server, int(port)))
   
    print('Server IP->'+str(server)+' Port->'+str(port))
    host = sock.getsockname()
    print('client IP->'+str(host[0])+' Port->'+str(host[1]))


except ConnectionRefusedError as c:
    print(c)
    print("Unable to connect")
    exit()


print("Enter required data")

while True:

    try:
        promt=input()
    except:
        print("Interrupted")
        exit()

    try:
        result=sock.send(promt.encode())
        if not result:
            raise Exception("No data!")
    except Exception as e:
        print(e)
        exit()

    try:
        data = sock.recv(1024).decode("utf8")
        if (len(data)==0):
            raise Exception("Lost connection")
        if ('exit' or 'sstop') in data.lower():
            raise MyExit("Disconnected")

    except ConnectionResetError as e:
        print("Lost connection from server")
        sock.close()
        exit()

    except MyExit as ex:
        print(ex)
        break
        exit()

    except Exception as s:
        print(s)
        sock.close()
        exit()

    

    print(data)

sock.close()

