from collections import namedtuple
from enum import Enum
import socket as s
from typing import NewType
import  KermitPacket
import constant

class KermitProtocol:

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

        self.send_init_params = ""

        for p in params:
            self.send_init_params += str(self.tochar(self.params[p]))

        # can be 0 -> receiver, 1 -> sender
        self.type = type
        socket_obj = NewType('socket_obj',s.socket())

        self.socket = socket_obj(socket)

        
        if (self.type == 0):
            self.current_state = constant.RECEIVESTATE.R
        else:
            self.current_state = constant.SENDSTATE.S
        
        #build a state table
        self.build_state()
        
        self.kermit_packet = KermitPacket.KermitPacket(self.type)

    def build_state(self,state,type):
        if type == 0:
            self.states  = {
            constant.SENDSTATE.S : (constant.SENDSTATE.S,constant.SENDSTATE.SF),
            constant.SENDSTATE.SF: (constant.SENDSTATE.SF,constant.SENDSTATE.SD),
            constant.SENDSTATE.SD: (constant.SENDSTATE.SD,constant.SENDSTATE.SD,constant.SENDSTATE.SZ),
            constant.SENDSTATE.SZ: (constant.SENDSTATE.SZ,constant.SENDSTATE.SZ,constant.SENDSTATE.SB),
            constant.SENDSTATE.SB: (constant.SENDSTATE.SB,constant.SENDSTATE.C)
        }
        else:
            self.states  = {
            constant.RECEIVESTATE.R : (constant.RECEIVESTATE.SF,constant.RECEIVESTATE.RF),
            constant.RECEIVESTATE.RF: (constant.RECEIVESTATE.RF,constant.RECEIVESTATE.RD),
            constant.RECEIVESTATE.RD: (constant.RECEIVESTATE.RD,constant.RECEIVESTATE.RF,constant.RECEIVESTATE.C),
        }

    def s_transit(self,_input):
        self.current_state = self.states[self.current_state][_input];
        packet = ""
        if self.current_state == constant.SENDSTATE.S:
            packet = self.kermit_packet.get_packet(constant.PACKET_TYPE.S,self.send_init_params)
        if self.current_state == constant.SENDSTATE.SF:
            packet = self.kermit_packet.get_packet(constant.PACKET_TYPE.F,self.chunk_file(constant.PACKET_TYPE.F,_input))
        if self.current_state == constant.SENDSTATE.D:
            packet == self.kermit_packet.get_packet(constant.PACKET_TYPE.D,self.chunk_file(constant.PACKET_TYPE.D,_input))
        if self.current_state == constant.SENDSTATE.SZ:
            packet == self.kermit_packet.get_packet(constant.PACKET_TYPE.Z,self.chunk_file(constant.PACKET_TYPE.Z,_input))
        if self.current_state == constant.SENDSTATE.SB:
            self.socket.shutdown()
            self.socket.close();
        self.socket.sendall(packet.encode())

    def r_transit(self,state,_input):
        self.current_state = self.states[self.previousState][_input];
        packet = ""
        if self.current_state == constant.RECEIVESTATE.R:
            packet = self.kermit_packet.get_packet(constant.PACKET_TYPE.S,self.send_init_params)
        if self.current_state == constant.RECEIVESTATE.RF:
            packet = self.kermit_packet.get_packet(constant.PACKET_TYPE.Y,self.chunk_file(constant.RECEIVESTATE.RF,_input))
        if self.current_state == constant.RECEIVESTATE.RD:
            packet == self.kermit_packet.get_packet(constant.RECEIVESTATE.RD,self.chunk_file(constant.RECEIVESTATE.RD,_input))
        if self.current_state == constant.RECEIVESTATE.C:
           print("DONE")

    
    def ack_receiver(self,ack):
        result = 0
        packet = self.kermit_packet.parse(ack)

        if packet["CORRECT"] == True:
            if packet["TYPE"] == constant.PACKET_TYPE.S:
                params = self.kermit_packet.parse_data(packet["DATA"],constant.PACKET_TYPE.P)

                
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
    
