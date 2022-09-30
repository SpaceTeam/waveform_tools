import sys
from time import time
sys.path.append('..')

from simulation_tools import COBC, update_time
from WF_Device import WF_Device
from CEP import CEP


if __name__ == '__main__':
    logan = WF_Device()
    logan.connect()

    cobc = COBC(logan, 0, 1, 2, 3, 4)

    cobc.edu_enable_pin.set_high()
    cobc.heartbeat_pin.wait_for('high', 10)

    cobc.uart.send(update_time(time()))
    cobc.uart.wait_for(CEP.ACK, 1)
    cobc.uart.wait_for(CEP.ACK, 1)
