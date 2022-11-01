from __future__ import annotations
from enum import Enum
from typing import List

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
    def parse_packet(raw: bytearray) -> CEP:
        """Attempts to parse the first packet present in the given bytearray"""
        if len(raw) == 0:
            raise ValueError("Empty bytearray")

        if raw[0] not in [e.value for e in CEP]:
            raise ValueError(f"Unknown first byte {hex(raw[0])}")

        if raw[0] != 0x8B:
            return CEP(raw[0])
        
        length = int.from_bytes(raw[1:3], byteorder='little')
        if len(raw) < length + 7:
            raise ValueError(f"Length field ({length}) longer than bytearray")
        
        data = raw[3:3+length]
        check = raw[3+length:3+length+4]
        if not CRC.verify_checksum(data, int.from_bytes(check, 'little')):
            raise ValueError(f"Invalid CRC: {check}")
        return CEP.with_data(data)

    @staticmethod
    def parse_multiple_packets(raw: bytearray) -> List[CEP]:
        """Attempts to parse all packets in the given bytearray"""
        packs = list()
        while len(raw) > 0:
            p = CEP.parse_packet(raw)
            raw = raw[len(p):]
            packs.append(p)
        return packs

    def serialize(self) -> bytearray:
        if self.name != "DATA":
            return bytearray(self.value)

        val = bytearray(0)
        val.append(self.value)
        val.extend(len(self.data).to_bytes(2, 'big'))
        val.extend(self.data)
        val.extend(CRC.calculate_checksum(self.data).to_bytes(4, 'big'))
        return val

    def __len__(self) -> int:
        if self.value != 0x8B:
            return 1
        else:
            return 7 + len(self.data)

    def __str__(self) -> str:
        if self.value != 0x8B:
            return f"<{self.name} {hex(self.value)}>"
        else:
            return f"<{self.name} with {len(self.data)} bytes>"


if __name__ == '__main__':
    arr = b'\x8b\x03\x00\x12\x34\x56\x57\x86\x98\xbe\xd7'
    print(CEP.parse_multiple_packets(arr))
