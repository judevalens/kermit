from enum import Enum
import constant
import os

class KermitPacket:

    def __init__(self, type: int, protocol, file_name: str = None):
        self.type = type
        self.packet_number = -1
        self.k_protocol = protocol;
        self.file_info  = constant.file_info
        self.chunk = None
        self.packet = None
        
    def get_packet(self, packet_type, data) -> str:

        if data == -1:
            return data
        
        if (self.k_protocol.state_input == 1) or (self.packet == None):

            self.packet_number += 1
            
            self.packet = str(self.tochar(self.ctl(1)))

            middle_packet = str(self.tochar((self.packet_number % 64))) + (str(packet_type)) + str(data)

            middle_packet_len = str(self.tochar(len(middle_packet)+1))
            middle_packet = middle_packet_len + middle_packet

            check = self.check_sum(middle_packet)
            print("CHECK ")
            print(check)
            
            middle_packet += str(self.tochar(check))
            self.packet += middle_packet

        return self.packet

    def parse_packet(self, _packet: bytes):
        packet = constant.packet
        _packet = _packet.decode()
        print("----------------PACKET PARSING------------")
        print(_packet)
        p_len = len(_packet)
        packet["MARK"] = _packet[:1]
        packet["LEN"] = self.unchar(_packet[1:2])
        packet["SEQ"] = self.unchar(_packet[2:3])
        packet["TYPE"] = _packet[3:4]
        packet["DATA"] = _packet[4:p_len-1]
        packet["CHECK"] =self.unchar(_packet[p_len-1:p_len])
        packet["CORRECT"] = self.check((_packet[1:(p_len-1)]), packet["CHECK"])
        return packet

    def parse_data(self, packet_type, _data):
        """
        parse the data field in a kermit packet
        
        """
        data = {}
        if packet_type == constant.PACKET_TYPE.S.name:
            data = constant.params                        
            data = {
            "MAXL": self.unchar(_data[0:1]),
            "TIME": self.unchar(_data[1:2]),
            "NPAD": self.unchar(_data[2:3]),
            "PADC": self.unchar(_data[3:4]),
            # EOL = ^M
            "EOL": self.unchar(_data[4:5]),
            "QCTL": _data[5:6],
            "QBIN": _data[6:7],
            "CHKT": self.unchar(_data[7:8]),
            "RPT": self.unchar(_data[8:9]),
            "CAPAS": self.unchar(_data[9:10])
        }

        return data

    def open_file(self,file_name):
        self.file  = open(file_name, "br")
        print("FIRST OPEN")
        print(self.file.read(int(self.k_protocol.params["MAXL"])-5))
        
        file_stats = os.stat(file_name)
        self.file_info['file_name'] = file_name
        self.file_info['file_size'] = file_stats.st_size
    
    def chunk_file(self,packet_type):
        if self.chunk == None or self.k_protocol.state_input != 0:
            if packet_type == constant.PACKET_TYPE.F.name:
                self.chunk = self.file_info["file_name"]
            elif packet_type == constant.PACKET_TYPE.D.name:
                self.chunk = self.file.read(int(self.k_protocol.params["MAXL"])-5)
                chunk_length = len(self.chunk)

                if chunk_length == 0:
                    self.chunk = -1
                    print("EOF")
                    self.k_protocol.socket.close()
        return self.chunk
    
    def write_file(self,packet_type,file_data):
        if packet_type == constant.PACKET_TYPE.F.name:
            self.file_info["file_name"] = file_data
            self.file = open("b"+self.file_info["file_name"], "wb")
        elif packet_type == constant.PACKET_TYPE.D.name:
            self.file.write(file_data)
        elif packet_type == constant.PACKET_TYPE.Z.name:
            self.file.close()
    
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
        n = x
        if n <= 32:
            n = n + 64
            n =  chr(n)
        return n

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