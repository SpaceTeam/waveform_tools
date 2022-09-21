from ctypes import *

from WF_Device import WF_Device

class WF_DIO:
    def __init__(self, device: WF_Device, pin: int, output_enable=False):
        if device.value == 0:
            raise ValueError("waveform device is not connected")
        self._d = device
        self._pin = pin
        self._output_enable = output_enable

        if output_enable:
            self.enable_output()

    def set_high(self):
        if not self._output_enable:
            raise ValueError(f"pin {self._pin} not set as output")

        mask = c_int()
        self._d._dwf.FDwfDigitalIOOutputGet(self._d._hdwf, byref(mask))
        self._d._dwf.FDwfDigitalIOOutputSet(self._d._hdwf, c_int(mask.value | (1 << self._pin)))

    def set_low(self):
        if not self._output_enable:
            raise ValueError(f"pin {self._pin} not set as output")

        mask = c_int()
        self._d._dwf.FDwfDigitalIOOutputGet(self._d._hdwf, byref(mask))
        self._d._dwf.FDwfDigitalIOOutputSet(self._d._hdwf, c_int(mask.value & ~(1 << self._pin)))

    def read(self):
        self._d._dwf.FDwfDigitalIOStatus(self._d._hdwf) # fetch new data
        status = c_int()
        self._d._dwf.FDwfDigitalIOInputStatus(self._d._hdwf, byref(status)) # actually read
        return (status & (1 << self._pin)) != 0

    def enable_output(self):
        mask = c_int()
        self._d._dwf.FDwfDigitalIOOutputEnableGet(self._d._hdwf, byref(mask))
        self._d._dwf.FDwfDigitalIOOutputEnableSet(self._d._hdwf, c_int(mask.value | (1 << self._pin)))