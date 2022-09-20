from ctypes import *
import sys
import logging

class WF_Device:
    def __init__(self):
        if sys.platform.startswith("win"):
            self._dwf = cdll.LoadLibrary("dwf.dll")
        elif sys.platform.startswith("darwin"):
            self._dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf"):
        else:
            self._dwf = cdll.LoadLibrary("libdwf.so")
        self._hdwf = c_int(0)

    def connect(self):
        logging.debug("Aquiring device...")
        self._dwf.FDwfDeviceOpen(c_int(-1), byref(self._hdwf))
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
