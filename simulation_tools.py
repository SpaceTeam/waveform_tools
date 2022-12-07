import logging

from .CEP import CEP
from .WF_Device import WF_Device
from .WF_Uart import WF_Uart
from .WF_DIO import WF_DIO


class COBC:
    def __init__(self, device: WF_Device, tx_pin: int, rx_pin: int, update_pin: int, edu_enable_pin: int, heartbeat_pin: int):
        self.device = device
        self.uart = WF_Uart(self.device, 921600, tx_pin, rx_pin, 8, 0, 1)
        self.update_pin = WF_DIO(self.device, update_pin, False)
        self.edu_enable_pin = WF_DIO(self.device, edu_enable_pin, True)
        self.heartbeat_pin = WF_DIO(self.device, heartbeat_pin, False)


def send_multi_packet(uart: WF_Uart, data: bytearray, timeout=1) -> None:
    logging.debug("Sending multipacket...")
    chunks = [data[i:i + 32768] for i in range(0, len(data), 32768)]
    for c in chunks:
        uart.send(CEP.with_data(c).serialize())
        ret = uart.receive(1, timeout)
        if ret != CEP.ACK.serialize():
            raise ValueError(f"Expected ACK but received {ret}")

    uart.send(CEP.EOF.serialize())
    ret = uart.receive(1, timeout)
    if ret != CEP.ACK.serialize():
        raise ValueError(f"Expected ACK but received {ret}")
    logging.debug("...successfuly")


def store_archive(program_id: int) -> CEP:
    return CEP.with_data(b'\x01' + program_id.to_bytes(2, 'big'))


def update_time(epoch: int) -> CEP:
    return CEP.with_data(b'\x06' + epoch.to_bytes(4, 'big'))
    