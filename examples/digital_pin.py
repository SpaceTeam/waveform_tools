from ..WF_Device import WF_Device
from ..WF_DIO import WF_DIO
import time

if __name__ == "__main__":
    logan = WF_Device()
    logan.connect()

    pin5 = WF_DIO(logan, 5, True) # connect to pin 5 of the logic analyzer and enable its output
    for _ in range(5):
        pin5.set_high()
        time.sleep(0.25)
        pin5.set_low()
        time.sleep(0.25)
