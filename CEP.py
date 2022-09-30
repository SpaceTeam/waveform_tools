from enum import Enum

from crc import CrcCalculator, Configuration

crc_config = Configuration(32, 0x04C11DB7, 0xffffffff)
CRC = CrcCalculator(crc_config)

class CEP(Enum):
    ACK = 0xD7
    NACK = 0x27
    EOF = 0x59
    STOP = 0xB4
    DATA = 0x8B

    @staticmethod
    def with_data(data: bytearray):
        obj = CEP.DATA
        obj.data = data
        return obj

    @staticmethod
    def from_bytes(raw: bytearray):
        if len(raw) == 1:
            return CEP(raw[0])
        if raw[0] != 0x8B:
            raise ValueError(f"Invalid package: {raw}")
        
        data = raw[3:-4]
        check = raw[-4:]
        if not CRC.verify_checksum(data, int.from_bytes(check, 'big')):
            raise ValueError(f"Invalid CRC: {raw}")
        return CEP.with_data(data)

    def serialize(self) -> bytearray:
        if self.name != "DATA":
            return bytearray(self.value)

        val = bytearray(0)
        val.append(self.value)
        val.extend(len(self.data).to_bytes(2, 'big'))
        val.extend(self.data)
        val.extend(CRC.calculate_checksum(self.data).to_bytes(4, 'big'))
        return val


if __name__ == '__main__':
    print(CEP.from_bytes(CEP.with_data(b"hello").serialize()))