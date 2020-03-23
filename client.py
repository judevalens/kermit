import socket
import KermitProtocol
import KermitPacket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect(('DESKTOP-E844T7N', 6000))

kermit = KermitProtocol.KermitProtocol(0,serversocket)

packet =  KermitPacket.KermitPacket(0,"d.txt");

while kermit.is_active:
    data = serversocket.recv(kermit.params["MAXL"])

    kermit.receiver(data)

