from enum import Enum

from crc import CrcCalculator, Configuration, Cr

crc_config = Configuration(32, 0x04C11DB7, 0xffffffff)
CRC = CrcCalculator(crc_config)

class CEP(Enum):
    ACK = 0xD7
    NACK = 0x27
    EOF = 0x59
    STOP = 0xB4
    DATA = 0x8B

    def __init__(self, data=None):
        if self.name != "DATA" and data != None:
            raise ValueError("Non DATA packet cant have data")
        self.data = data

    def serialize(self) -> bytearray:
        if self.name != "DATA":
            return bytearray(self.value)

        val = bytearray(self.value)
        val.extend(len(self.data).to_bytes(2, 'big'))
        val.extend(self.data)
        val.extend(CRC.calculate_checksum(self.data).to_bytes(4, 'big'))
        return val    

