from ctypes import *
import sys
import logging

class WF_Device:
    """ A wrapper for any waveform supported device.
    Do not forget to call connect()
    """

    def __init__(self):
        try:
            if sys.platform.startswith("win"):
                self._dwf = cdll.LoadLibrary("dwf.dll")
            elif sys.platform.startswith("darwin"):
                self._dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf"):
            else:
                self._dwf = cdll.LoadLibrary("libdwf.so")
        except OSError:
            logging.fatal("Could not load library, is WaveForms installed?")
            raise
        self._hdwf = c_int(0)

    def connect(self, device_index=-1):
        """Attempts to connect to a waveform device.
        Specifying the device index allows to connect to a specific one;
        otherwise the first one that is detected is used.
        """
        logging.debug("Aquiring device...")
        self._dwf.FDwfDeviceOpen(c_int(device_index), byref(self._hdwf))
        if self._hdwf.value == 0:
            logging.error("Faild to open device")
            szerr = create_string_buffer(512)
            self._dwf.FDwfGetLastErrorMsg(szerr)
            logging.error(str(szerr.value))
            raise ConnectionError()

    def reset(self):
        if self._hdwf.value == 0:
            logging.error("No device connected to reset")
            return
        self._dwf.FDwfDeviceReset(self._hdwf)

    def close(self):
        self._dwf.FDwfDeviceCloseAll()
