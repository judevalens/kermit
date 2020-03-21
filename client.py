import socket
import KermitProtocol
import KermitPacket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect(('DESKTOP-E844T7N', 6000))

kermit = KermitProtocol.KermitProtocol(0,serversocket)

packet =  KermitPacket.KermitPacket(0,"d.txt");


active  = True

while active:
    data = serversocket.recv(1024)
    print("pass")
    print(data.decode('utf-8'))
    kermit.receiver(data)

