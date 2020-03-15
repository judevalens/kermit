from enum import Enum
import constant

class KermitPacket:
    
    def __init__(self, type):
        self.type = type
        self.packet_number = -1;
        self.states  = {
            constant.SENDSTATE.S : (constant.SENDSTATE.SF,constant.SENDSTATE.SF)
        }

    def get_packet(self,packet_type,data)->str:
        self.packet_number += 1;
        packet = str(self.tochar(self.ctl(1)))
        middle_packet = str(self.tochar((self.packet_number % 64))) + (str(packet_type)) + str(data)
        check = str(self.check_sum(middle_packet))
        middle_packet += check
        packet += str(len(middle_packet))+middle_packet

        return packet

    def parse(self,packet):
        packet = constant.packet
        
        packet["MARK"] = self.unctl(self.tochar(packet[:1]))
        packet["LEN"] = self.unctl(self.tochar(packet[1:2]))
        packet["SEQ"] = self.unctl(self.tochar(packet[2:3]))
        packet["TYPE"] = self.unctl(self.tochar(packet[3:4]))
        packet["DATA"]  = self.unctl(self.tochar(packet[4:packet["LEN"]-1]))
        packet["CHECK"] = self.unctl(self.tochar(packet[packet["LEN"]-1:packet["LEN"]]))
        packet["CORRECT"] = self.check(packet[1:packet["LEN"]-1])
        return packet
    
    def parse_data(self,data_type):
        if data_type == constant.DATA_TYPE.P:
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

    def check(self,string,expected_sum)->bool:
        current_sum = self.check_sum(string)

        return current_sum == expected_sum