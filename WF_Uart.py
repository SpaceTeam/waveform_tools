from ctypes import *
import time
from .CEP import CEP
from .WF_Device import WF_Device
import logging


class WF_Uart:
    def __init__(self, device: WF_Device, baudrate: int, tx_pin: int, rx_pin: int, bits_per_word: int, parity: int, stop_length: int):
        """Initializes a UART protocol on the given tx and rx pins. 
        The parity bit can be set to 0 - No parity bit, 1 - odd, 2 - even
        """
        if device._hdwf.value == 0:
            raise ValueError("waveform device is not connected")
        
        logging.debug(f"Configuring UART with TX {tx_pin}, RX {rx_pin}, baud {baudrate}, {bits_per_word}N{stop_length}S, {parity} parity")
        self._d = device
        self._d._dwf.FDwfDigitalUartRateSet(self._d._hdwf, c_double(baudrate))
        self._d._dwf.FDwfDigitalUartTxSet(self._d._hdwf, c_int(tx_pin)) 
        self._d._dwf.FDwfDigitalUartRxSet(self._d._hdwf, c_int(rx_pin)) 
        self._d._dwf.FDwfDigitalUartBitsSet(self._d._hdwf, c_int(bits_per_word))
        self._d._dwf.FDwfDigitalUartParitySet(self._d._hdwf, c_int(parity))
        self._d._dwf.FDwfDigitalUartStopSet(self._d._hdwf, c_double(stop_length))

        self._rx_count = c_int(0)
        self._rx_parity = c_int(0)
        self._d._dwf.FDwfDigitalUartTx(self._d._hdwf, None, c_int(0)) # initialize TX, drive with idle level
        self._d._dwf.FDwfDigitalUartRx(self._d._hdwf, None, c_int(0), byref(self._rx_count), byref(self._rx_parity)) # initialize RX reception
        self._d.check_for_error()

    def send(self, data: bytearray):
        logging.debug(f"Sending {data}...")
        if isinstance(data, CEP):
            data = data.serialize()
        rgTX = create_string_buffer(len(data)+1)
        rgTX.value = bytes(data)
        self._d._dwf.FDwfDigitalUartTx(self._d._hdwf, rgTX, c_int(sizeof(rgTX)-1)) # send data, cut off \0
        self._d.check_for_error()

    def receive(self, n_bytes: int, timeout: float) -> bytearray:
        """Attempts to receive the given number of bytes within a timeout given in seconds.
        This function is blocking
        """
        logging.debug(f"Attempting to receive {n_bytes} bytes in {timeout:.2f}s")
        rgRX = create_string_buffer(n_bytes+1)
        buffer = bytearray()
        end_time = time.perf_counter() + timeout

        while time.perf_counter() < end_time:
            self._d._dwf.FDwfDigitalUartRx(self._d._hdwf, rgRX, c_int(sizeof(rgRX)), byref(self._rx_count), byref(self._rx_parity))
            if self._rx_count.value > 0:
                logging.debug(f"Received {self._rx_count.value} bytes")
                buffer.extend(rgRX.raw[:self._rx_count.value])
            if self._rx_parity.value != 0:
                raise ParityError(f"Failed with {self._rx_parity.value}; received {rgRX.raw}")
            time.sleep(0.01)
        self._d.check_for_error()

        if len(buffer) < n_bytes:
            raise TimeoutError(f"Received data only up to {buffer}")

        return buffer

    def wait_for(self, expected: bytearray, timeout: float) -> None:
        """Attempts to receive the expected data. Raises a Value/TimeoutError if not successful"""
        logging.debug(f"Uart waiting for {expected}...")
        if isinstance(data, CEP):
            data = data.serialize()
        ret = self.receive(len(expected), timeout)
        if ret != expected:
            raise ValueError(f"Expected {expected} but received {ret}")

class ParityError(Exception):
    pass  