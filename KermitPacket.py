from enum import Enum
import constant


class KermitPacket:

    def __init__(self, type):
        self.type = type
        self.packet_number = -1
        self.states = {
            constant.SENDSTATE.S: (constant.SENDSTATE.SF,
                                   constant.SENDSTATE.SF)
        }

    def get_packet(self, packet_type, data) -> str:
        self.packet_number += 1
        packet = str(self.tochar(self.ctl(1)))

        middle_packet = str(self.tochar((self.packet_number % 64))) + (str(packet_type)) + str(data)

        middle_packet_len = str(self.tochar(len(middle_packet)+1))
        middle_packet = middle_packet_len + middle_packet


        check = self.check_sum(middle_packet)
        print("CHECK ")
        print(check)
        
        middle_packet += str(self.tochar(check))
        packet += middle_packet
        return packet

    def parse_packet(self, _packet: bytes):
        packet = constant.packet
        _packet = _packet.decode()
        p_len = len(_packet)
        packet["MARK"] =_packet[:1]
        packet["LEN"] = _packet[1:2]
        packet["SEQ"] = _packet[2:3]
        packet["TYPE"] = _packet[3:4]
        packet["DATA"] = _packet[4:p_len-1]
        packet["CHECK"] =_packet[p_len-1:p_len]
        packet["CORRECT"] = self.check((_packet[1:(p_len-1)]), self.unchar(packet["CHECK"]))
        return packet

    def parse_data(self, data_type, _data):
        """
        parse the data field in a kermit packet
        
        """
        data = {}
        if data_type == constant.PACKET_TYPE.S.name:
            data = constant.params
            i = 0
            for f in data:
                data[f] = _data[i]
                i += 1
        return data

    # util functions
    def tochar(self, n) -> str:
        x = n
        if isinstance(n, int) == True:
            x = n + 32
            x = chr(x)
        return x

    def unchar(self, c) -> int:
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

    def ascii_sum(self, string) -> int:
        s = 0
        for c in string:
            s += ord(c)
        return s

    def check_sum(self, string) -> int:
        s = self.ascii_sum(string)  # 1 accounts for the LEN
        check = ((s + ((s & 192)//64)) & 63)
        return check

    def check(self, string, expected_sum) -> bool:
        current_sum = self.check_sum(string)
        print("current_sum " + str(current_sum))
        print("expected_sum " + str(expected_sum))
        return current_sum == expected_sum
