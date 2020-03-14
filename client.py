import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect(('DESKTOP-E844T7N', 6000))
serversocket.send(b"start !!!!!!!!!!!! !")

kermit = KermitProtocol.KermitProtocol(0,serversocket)


while True:
    data = serversocket.recv(1024)
    kermit.dispatcher(data)
    print(data.decode('utf-8'))
    serversocket.send(b"received!!!!!!!!!!!!!")
