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

        # can be 0 -> receiver, 1 -> sender
        self.type = _type
        socket_obj = NewType('socket_obj', s.socket())

        self.socket = socket_obj(socket)
        self.kermit_packet = KermitPacket.KermitPacket(self.type)
        self.build_state(self.type)

        if (self.type == 0):
            self.current_state = constant.RECEIVESTATE.R
        else:
            self.current_state = constant.SENDSTATE.S
            self.s_transit(0)

        # build a state table

    def build_state(self, type):
        if type == 1:
            print("SENDER")
            self.states = {
                constant.SENDSTATE.S: (constant.SENDSTATE.S, constant.SENDSTATE.SF),
                constant.SENDSTATE.SF: (constant.SENDSTATE.SF, constant.SENDSTATE.SD),
                constant.SENDSTATE.SD: (constant.SENDSTATE.SD, constant.SENDSTATE.SD, constant.SENDSTATE.SZ),
                constant.SENDSTATE.SZ: (constant.SENDSTATE.SZ, constant.SENDSTATE.SZ, constant.SENDSTATE.SB),
                constant.SENDSTATE.SB: (
                    constant.SENDSTATE.SB, constant.SENDSTATE.C)
            }
        else:
            print("RECEIVER")
            self.states = {
                constant.RECEIVESTATE.R: (constant.RECEIVESTATE.RF, constant.RECEIVESTATE.RF),
                constant.RECEIVESTATE.RF: (constant.RECEIVESTATE.RF, constant.RECEIVESTATE.RD),
                constant.RECEIVESTATE.RD: (constant.RECEIVESTATE.RD, constant.RECEIVESTATE.RF, constant.RECEIVESTATE.C),
            }

    def s_transit(self, _input):
        self.current_state = self.states[self.current_state][_input]
        packet = ""
        if self.current_state == constant.SENDSTATE.S:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.S.name, self.send_init_params)
        if self.current_state == constant.SENDSTATE.SF:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.F.name, self.chunk_file(constant.PACKET_TYPE.F.name, _input))
        if self.current_state == constant.SENDSTATE.SD:
            packet == self.kermit_packet.get_packet(
                constant.PACKET_TYPE.D.name, self.chunk_file(constant.PACKET_TYPE.D.name, _input))
        if self.current_state == constant.SENDSTATE.SZ:
            packet == self.kermit_packet.get_packet(
                constant.PACKET_TYPE.Z.name, self.chunk_file(constant.PACKET_TYPE.Z.name, _input))
        if self.current_state == constant.SENDSTATE.SB:
            print("SHUTDOWN")
            self.socket.shutdown()
            self.socket.close()
        print("SENDING " + packet)
        self.socket.sendall(packet.encode())

    def r_transit(self, state, _input):
        self.current_state = self.states[self.previousState][_input]
        packet = ""
        if self.current_state == constant.RECEIVESTATE.R:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.S, self.send_init_params)
        if self.current_state == constant.RECEIVESTATE.RF:
            packet = self.kermit_packet.get_packet(
                constant.PACKET_TYPE.Y, self.chunk_file(constant.RECEIVESTATE.RF, _input))
        if self.current_state == constant.RECEIVESTATE.RD:
            packet == self.kermit_packet.get_packet(
                constant.RECEIVESTATE.RD, self.chunk_file(constant.RECEIVESTATE.RD, _input))
        if self.current_state == constant.RECEIVESTATE.C:
            print("DONE")

    def ack_receiver(self: object, ack: str) -> None:
        """
        Receive an acknowledgement packet from the receiver and call the s_transit with the approriate input.

        Parameters:

            ack (str): represents a packet.
        """
        print("ACK")
        result = 0
        packet = self.kermit_packet.parse_packet(ack)

        if packet["CORRECT"] == True:
            if packet["TYPE"] == constant.PACKET_TYPE.S.name:
                self.params = self.kermit_packet.parse_data(
                    packet["DATA"], constant.DATA_TYPE.P.name)
                result = 1
            elif packet["TYPE"] == constant.PACKET_TYPE.Y.name:
                result = 1
            else:
                result = 0
        print("P LAST")
        self.s_transit(result)

    def receiver(self, _packet):
        packet = self.kermit_packet.parse_packet(_packet)
        packet_data = self.kermit_packet.parse_data(
            packet["TYPE"], packet["DATA"])
        r_packet = {}
        if packet["CORRECT"] == True:
            if packet["TYPE"] == constant.PACKET_TYPE.S.name:
                # I should be comparing the data and adjust them them | going to use the defaut params instead :) i will fix that
                if packet["TYPE"] == constant.PACKET_TYPE.S.name:
                    r_packet = self.kermit_packet.get_packet(
                        constant.PACKET_TYPE.S.name, self.send_init_params)
        else:
            r_packet = self.kermit_packet.get_packet(constant.PACKET_TYPE.N,"")
        self.socket.sendall(r_packet.encode())
                    

        print(str(packet))
        print("packet_data")
        print(str(packet_data))

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
