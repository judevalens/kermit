import socket
import KermitProtocol

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((socket.gethostname(), 6000))
serversocket.listen(5)
print("gethostname " + socket.gethostname() +"\n")

(client_socket, address) = serversocket.accept()

print("client_socket " + str(client_socket) +"\n")
print("address " + str(address) +"\n")

activate_connection = True
kermit = KermitProtocol.KermitProtocol(1,client_socket)
count  = 0;
while activate_connection:
    kermit.s_send();
    data = client_socket.recv(1024)
    print(data)
    #count += 1;
    #str_to_send = "packet # " + str(count) +"\n"
    #byte = str_to_send.encode();
    #client_socket.sendall(byte);
