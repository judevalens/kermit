from collections import namedtuple
from enum import Enum
import socket as s
from typing import NewType
import KermitPacket
import constant


class KermitProtocol:

    def __init__(self, _type, socket, MAXL=80, TIME=5, NPAD=0, PADC=0, EOL=13, QCTL='#', QBIN=' ', CHKT=1, RPT=0, CAPAS=0):
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

        for p in self.params:
            self.send_init_params += str(self.tochar(self.params[p]))

        self.state_input = 0

        # can be 0 -> receiver, 1 -> sender
        self.type = _type
        socket_obj = NewType('socket_obj', s.socket())

        self.socket = socket_obj(socket)
        self.kermit_packet = KermitPacket.KermitPacket(self.type, self)
        self.build_state(self.type)

        if (self.type == 0):
            self.current_state = constant.RECEIVESTATE.R
        else:
            self.current_state = constant.SENDSTATE.S
            self.s_transit()

        # build a state table

    def build_state(self, type):
        if type == 1:
            print("SENDER")
            self.states = {
                constant.SENDSTATE.S: (constant.SENDSTATE.S, constant.SENDSTATE.SF),
                constant.SENDSTATE.SF: (constant.SENDSTATE.SF, constant.SENDSTATE.SD),
                constant.SENDSTATE.SD: (constant.SENDSTATE.SD, constant.SENDSTATE.SD, constant.SENDSTATE.SZ),
                constant.SENDSTATE.SZ: (constant.SENDSTATE.SZ, constant.SENDSTATE.SB),
                constant.SENDSTATE.SB: (
                    constant.SENDSTATE.SB, constant.SENDSTATE.C)
            }
        else:
            print("RECEIVER")
            self.states = {
                constant.RECEIVESTATE.R: (constant.RECEIVESTATE.R, constant.RECEIVESTATE.RF),
                constant.RECEIVESTATE.RF: (constant.RECEIVESTATE.RF, constant.RECEIVESTATE.RD),
                constant.RECEIVESTATE.RD: (constant.RECEIVESTATE.RD, constant.RECEIVESTATE.RF, constant.RECEIVESTATE.C),
            }

    def s_transit(self):
        self.current_state = self.states[self.current_state][self.state_input]
        packet = ""
        if self.current_state == constant.SENDSTATE.S:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.S.name, self.send_init_params)
        if self.current_state == constant.SENDSTATE.SF:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.F.name, self.kermit_packet.chunk_file(constant.PACKET_TYPE.F.name))
        if self.current_state == constant.SENDSTATE.SD:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.D.name, self.kermit_packet.chunk_file(constant.PACKET_TYPE.D.name))
            if packet == -1:
                print("=============END OF FILE")
                self.state_input = 2
                self.s_transit()
                return
        if self.current_state == constant.SENDSTATE.SZ:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.Z.name, "")
        if self.current_state == constant.SENDSTATE.SB:
            print("SHUTDOWN")
            self.socket.shutdown()
            self.socket.close()
            return
        print("SENDING " + packet)
        self.socket.sendall(packet.encode())

    def r_transit(self):
        self.current_state = self.states[self.current_state][self.state_input]

        if self.current_state == constant.RECEIVESTATE.R:
            pass

    def ack_receiver(self: object, ack: str) -> None:
        """
        Receive an acknowledgement packet from the receiver and call the s_transit with the approriate input.

        Parameters:

            ack (str): represents a packet.
        """
        print("ACK")
        self.state_input = 0
        packet = self.kermit_packet.parse_packet(ack)
        print(packet)

        if packet["CORRECT"] == True:
            if packet["TYPE"] == constant.PACKET_TYPE.S.name:
                self.params = self.kermit_packet.parse_data(
                    packet["TYPE"], packet["DATA"])
                self.state_input = 1
                print("PARAM")
                print(str(self.params))
            elif packet["TYPE"] == constant.PACKET_TYPE.Y.name:
                print("PARAM Y ACK")
                self.state_input = 1
            else:
                self.state_input = 0
        print("P LAST")
        self.s_transit()

    def receiver(self, _packet):
        print("PACKET RECEIVED")
        print(_packet)
        packet = self.kermit_packet.parse_packet(_packet)
       
        if packet["CORRECT"] == True:
            self.state_input = 1
            if packet["TYPE"] == constant.PACKET_TYPE.S.name:
                packet_data = self.kermit_packet.parse_data(packet["TYPE"], packet["DATA"])
                # I should be comparing the data and adjust them them | going to use the defaut params instead :) i will fix that
                r_packet = self.kermit_packet.get_packet(
                    constant.PACKET_TYPE.S.name, self.send_init_params)
                self.socket.sendall(r_packet.encode())
                return
            elif packet["TYPE"] == constant.PACKET_TYPE.F.name:
                self.kermit_packet.write_file(packet["TYPE"], packet["DATA"])
            elif packet["TYPE"] == constant.PACKET_TYPE.D.name:
                self.kermit_packet.write_file(packet["TYPE"], packet["DATA"].encode())
            elif packet["TYPE"] == constant.PACKET_TYPE.Z.name:
                self.kermit_packet.write_file(packet["TYPE"], -1)

        else:
            self.state_input = 0

        packet_type = constant.PACKET_TYPE.Y.name
        if self.state_input == 0:
            packet_type = constant.PACKET_TYPE.N.name
        ack_packet = self.kermit_packet.get_packet(packet_type, "")
        self.socket.sendall(ack_packet.encode())

    def tochar(self, n):
        if isinstance(n, int) == True:
            n = n + 32
            n = chr(n)
        return n

    def unchar(self, c):
        if isinstance(c, str) == True:
            c = ord(c)
            c = c - 32
        return c

    def ctl(self, x) -> str:
        x = x + 64
        return chr(x)

    def unctl(self, x) -> int:
        x = ord(x) - 64
        return x

    def open_file(self, path):
        self.kermit_packet.open_file(path)
