from ctypes import c_int, byref
import logging
import time
from typing import Literal

from .WF_Device import WF_Device


class WF_DIO:
    def __init__(self, device: WF_Device, pin: int, output_enable=False):
        if device._hdwf.value == 0:
            raise ValueError("waveform device is not connected")
        self._d = device
        self._pin = pin
        self._output_enable = output_enable

        if output_enable:
            self.enable_output()

    def set_high(self):
        logging.debug(f"setting pin {self._pin} to high")
        if not self._output_enable:
            raise ValueError(f"pin {self._pin} not set as output")

        mask = c_int()
        self._d._dwf.FDwfDigitalIOOutputGet(self._d._hdwf, byref(mask))
        self._d._dwf.FDwfDigitalIOOutputSet(self._d._hdwf, c_int(mask.value | (1 << self._pin)))

    def set_low(self):
        logging.debug(f"setting pin {self._pin} to low")
        if not self._output_enable:
            raise ValueError(f"pin {self._pin} not set as output")

        mask = c_int()
        self._d._dwf.FDwfDigitalIOOutputGet(self._d._hdwf, byref(mask))
        self._d._dwf.FDwfDigitalIOOutputSet(self._d._hdwf, c_int(mask.value & ~(1 << self._pin)))

    def read(self) -> bool:
        self._d._dwf.FDwfDigitalIOStatus(self._d._hdwf)  # fetch new data
        status = c_int()
        self._d._dwf.FDwfDigitalIOInputStatus(self._d._hdwf, byref(status))  # actually read
        return (status.value & (1 << self._pin)) != 0

    def enable_output(self) -> None:
        logging.debug(f"enabling output for pin {self._pin}")
        mask = c_int()
        self._d._dwf.FDwfDigitalIOOutputEnableGet(self._d._hdwf, byref(mask))
        self._d._dwf.FDwfDigitalIOOutputEnableSet(self._d._hdwf, c_int(mask.value | (1 << self._pin)))

    def wait_for(self, status: Literal['high', 'low'], timeout: float) -> None:
        logging.debug(f"Waiting {timeout:.2f}s for {self._pin} to be {status}")
        start = time.time()
        while (time.time() - start) < timeout:
            if self.read() is (status == "high"):
                return
            time.sleep(0.01)

        raise TimeoutError(f"Pin {self._pin} was not set to {status} within {timeout:.2f}")

    def expect_to_be(self, status: Literal['high', 'low']) -> None:
        if self.read() is not (status == 'high'):
            raise ValueError(f"Expected pin {self._pin} to be {status}")
