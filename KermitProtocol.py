from collections import namedtuple
from enum import Enum
import socket as s
from typing import NewType
import  KermitPacket

class SENDSTATE(Enum):
    S = "S"
    SF = "SF"
    SD = "SD"
    SZ = "SZ"
    SB = "SB"
    A = "A"
    C = "C"


class RECEIVESTATE(Enum):
    R = "R"
    RF = "RF"
    RD = "RD"
    A = "A"
    C = "C"


class KermitProtocol:
    socket_obj = NewType('socket_obj', s.socket())

    def __init__(self, type, socket, MAXL=80, TIME=5, NPAD=0, PADC=0, EOL=13, QCTL='#', QBIN=' ', CHKT=1, RPT=0, CAPAS=0):
        """
        create Send-Init packet on the first transaction
        """
        self.params = {
            "MAXL": MAXL,
            "TIME": TIME,
            "NPAD": NPAD,
            "PADC": PADC,
            # EOL = ^M
            "EOL": self.ctl(EOL),
            "QCTL": QCTL,
            "QBIN": QBIN,
            "CHKT": CHKT,
            "RPT": RPT,
            "CAPAS": CAPAS
        }
        # can be 0 -> receiver, 1 -> sender
        self.type = type
        self.socket = KermitProtocol.socket_obj(socket)
        if (self.type == 0):
            self.state = RECEIVESTATE.R
        else:
            self.state = SENDSTATE.S
        
        self.packet = KermitPacket.KermitPacket(self.type)


    def send_init(self) -> str:
        s_packet = ""
        for p in self.params:
            s_packet += str(self.params[p])
        return s_packet

    def tochar(self, x):
        x = x + 32
        x  = chr(x)
        return x

    def unchar(self, x):
        x = ord(x) 
        x = x - 32
        return x 

    def ctl(self, x) -> str:
        x = x + 64
        return chr(x)

    def unctl(self, x) -> int:
        x = ord(x) - 64
        return x
    def dispatcher(self, packet=None):
        if(self.type == 0):
            if self.state == RECEIVESTATE.R:
                params = packet.parse(packet)
                
    def receive(self, packet):
        if state == RECEIVESTATE.R:
            self.socket.sendall(self.send_init().encode())
        p

    def s_send(self) -> None:
        self.socket.sendall(self.send_init().encode())
