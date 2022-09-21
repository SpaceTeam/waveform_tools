import sys
sys.path.append('..')
from WF_Device import WF_Device
from WF_Uart import WF_Uart

if __name__ == "__main__":
    logan = WF_Device()
    logan.connect()

    uart = WF_Uart(logan, baudrate=115200, tx_pin=0, rx_pin=1, bits_per_word=8, parity=2, stop_length=1)
    uart.send(b'\x00\x01\x02')
    print(uart.receive(3, 1))