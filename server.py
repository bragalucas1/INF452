import socket
import threading
import re

#Lucas Braga Moura - 98909
#Marco Aurélio Abrantes - 98887

IP = socket.gethostbyname(socket.gethostname())
TCP = 20000
ADDR = (IP, TCP)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "/bye"
LIST_USERS_CONNECTED_MSG = "/list"
SEND_FILE_MSG = '/file'
GET_FILE_MSG = '/get'



usernameByAddress = dict()
activeUsers = []
udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def handle_client():
    udp.bind(ADDR)

    tcp.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp.bind(ADDR)
    tcp.listen(1)
    connected = True
    while connected:
        msg, client  = udp.recvfrom(SIZE)
        msg = msg.decode(FORMAT)

        if msg == DISCONNECT_MSG:
            disconectUser(client)

        elif 'USER:' in msg:
            getClientName(msg, client)
        
        elif msg == LIST_USERS_CONNECTED_MSG:
            listActiveUsers(client)
        
        elif SEND_FILE_MSG in msg:
            sendFileMessage(msg, client)
        
        elif GET_FILE_MSG in msg:
            getFileFromServer(msg, client)
        else:
            sendTextMessage(msg, client)

def getClientName(msg, client):
    regexp = re.compile('USER:(.*)$')
    name = regexp.search(msg).group(1)
    activeUsers.append(name)
    usernameByAddress[client] = name
    msg = name + ' entrou'
    print('INFO:' + name + ' entrou')
    sendMensageToAll(msg, client)

def disconectUser(client):
    msg = usernameByAddress[client] + ' saiu'
    print('INFO:' + usernameByAddress[client] + ' saiu')
    sendMensageToAll(msg, client)
    activeUsers.remove(usernameByAddress[client])
    del usernameByAddress[client]

def listActiveUsers(client):
    msg = 'Clientes conectados:\n'
    for user in activeUsers:
        msg += user
        msg += ', '
    msg = msg[:-2]
    sendMessageToClient(msg, client)

def sendTextMessage(msg, client):
    print('MSG:' + usernameByAddress[client] + ':' + msg)
    clientMsg = 'MSG:' + msg
    msg = usernameByAddress[client] + ' disse: ' + msg
    sendMessageToClient(clientMsg, client)
    sendMensageToAll(msg, client)

def sendFileMessage(msg, client):
    regexp = re.compile('/file(.*)$')
    fileName = regexp.search(msg).group(1)
    fileName = fileName.strip()
    clientMsg = 'FILE:' + fileName
    sendMessageToClient(clientMsg, client)
    fileNameServ = ''.join(['serv-',fileName])
    udpClient = client
    conn, client = tcp.accept()
    file = open(fileNameServ, 'wb')
    data = conn.recv(SIZE*8) #Aumentamos o size do arquivo para que comportasse todo o código alvo.
    file.write(data)

    file.close()
    conn.close()

    print('INFO:' + usernameByAddress[udpClient] + ' enviou ' + fileName)
    msg = usernameByAddress[udpClient] + ' enviou ' + fileName
    sendMensageToAll(msg, udpClient)

def getFileFromServer(msg,client):
    regexp = re.compile('/get(.*)$')
    fileName = regexp.search(msg).group(1)
    fileName = fileName.strip()
    clientMsg = 'GET:' + fileName
    sendMessageToClient(clientMsg, client)
    conn, client = tcp.accept()
    file = open(fileName, 'rb')
    data = file.read()
    conn.send(data)

    file.close()
    conn.close()


def sendMessageToClient(msg, client):
    msg = msg.encode(FORMAT)
    udp.sendto(msg, client)
    return

def sendMensageToAll(msg, client):
    for user in usernameByAddress:
        if user != client:
            sendMessageToClient(msg, user)

def main():
    print(f"[NEW CONNECTION] {ADDR} connected")
    thread = threading.Thread(target=handle_client)
    thread.start()

main()
