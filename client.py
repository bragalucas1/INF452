import socket
import threading
import sys

#Lucas Braga Moura - 98909
#Marco Aurélio Abrantes - 98887

IP = socket.gethostbyname(socket.gethostname())
PORT = 20000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "/bye"
LIST_MSG = "/list"
SEND_FILE_MSG = '/file'
GET_FILE_MSG = '/get'

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendNameToServer():
    udp.connect(ADDR)
    nomeDeUsuario = input("Nome de usuario: ")
    msg = ("USER:" + nomeDeUsuario)
    udp.send(msg.encode(FORMAT))

def sendMessage():
    connect = True
    while connect:
        msg = input()

        if msg == DISCONNECT_MSG:
            udp.connect(ADDR)
            udp.send(msg.encode(FORMAT))
            udp.close()            
            connect = False
        
        elif SEND_FILE_MSG in msg:
            udp.send(msg.encode(FORMAT))
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect(ADDR)
            fileName = msg.split()[1]
            file = open(fileName,'rb')
            data = file.read()
            tcp.send(data)
            tcp.close()
            file.close()

        elif GET_FILE_MSG in msg:
            udp.send(msg.encode(FORMAT))
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect(ADDR)
            fileName = msg.split()[1]
            fileNameClient = ''.join(['client-',fileName])
            file = open(fileNameClient,'wb')
            data = tcp.recv(SIZE*8)
            file.write(data)
            file.close()
            tcp.close()

        else:
            udp.connect(ADDR)
            udp.send(msg.encode(FORMAT))

def receiveMessage():
    connect = True
    while connect:
        msg = udp.recv(SIZE).decode(FORMAT)
        print(msg)

sendNameToServer()

(threading.Thread(target=sendMessage)).start()
(threading.Thread(target=receiveMessage)).start()