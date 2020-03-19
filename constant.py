from enum import Enum

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
    A = "A" #"File attributes"

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

class DATA_TYPE(Enum):
    P = "P" #Paramaters
    R = "R" #Raw file data
    A = "A" #File Attributes
    F = "F" #File Header

packet = {
    "MARK":None,
    "LEN": None,
    "SEQ": None,
    "TYPE": None,
    "DATA":None,
    "CHECK":None,
    "CORRECT3": None
}


params = {
    "MAXL": None,
    "TIME": None,
    "NPAD": None,
    "PADC": None,
    # EOL = ^M
    "EOL": None,
    "QCTL": None,
    "QBIN": None,
    "CHKT": None,
    "RPT": None,
    "CAPAS": None
        }