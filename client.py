import socket
import KermitProtocol

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect(('DESKTOP-E844T7N', 6000))

kermit = KermitProtocol.KermitProtocol(0,serversocket)


while True:
    data = serversocket.recv(1024)
    print("pass")
    print(data.decode('utf-8'))
    kermit.receiver(data)
    serversocket.close()

