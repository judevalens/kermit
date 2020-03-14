from enum import Enum


class KermitPacket:
    class PACKET_TYPE(Enum):
        D = "D" #"Data Packet"
        Y = "Y" #"Acknowledge"
        N = "N" #"Negative Acknowledge"
        S = "S" #"Send Initiate"
        B = "B" #"Break Transmision"
        F = "F" #"File Header"
        Z = "Z" #"End OF File"
        E = "E" #"Error"
        Q = "Q" #"Undefined"
        T = "T" #"Undefined"

    class ACKNOWLEDGE_TYPE(Enum):
        G = "G" #GOOD
        B = "B" #BAD

    def __init__(self, type):
        self.type = type
        self.packet_number = -1;

    def get_packet(self,packet_type,data)->str:
        packet = str(self.ctl(1))
        middle_packet = str(self.tochar((self.packet_number % 64))) + (str(packet_type)) + str(data)
        check = str(self.check_sum(middle_packet))
        middle_packet += check
        packet += str(len(middle_packet))+middle_packet

        return packet

    def parse(self,packet):
        base_type  = packet[:1]
        base_type = self.unchar(base_type)
        pass
    #util functions
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
    
    def ascii_sum(self,string)->int:
        s =0
        for c in string:
            s += ord(c)
        return s

    def check_sum(self,string)->int:
        s = self.ascii_sum(string)+1 # 1 accounts for the LEN 
        check = ((s + ((s & 192)/64)) & 63)
        check = self.tochar(check)
        return check
