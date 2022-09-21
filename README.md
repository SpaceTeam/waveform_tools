# Waveform Tools
Logic Analyzers from Digilent (such as the Analog Discovery 2) can be used with the WaveForms software, which comes with a nice library. The scripts in this repository wrap it in an easy to use python API, which can then be used to automate test.

### Prerequisites
- Python 3
- WaveForms (https://digilent.com/shop/software/digilent-waveforms/download)

### How to use
Connect the logic analyzer to power and your PC. Then do something like this:
```python
logan = WF_Device()
logan.connect()

pin5 = WF_DIO(logan, 5, True) # connect to pin 5 of the logic analyzer and enable its output
pin5.set_high()

uart = WF_Uart(logan, baudrate=115200, tx_pin=0, rx_pin=1, bits_per_word=8, parity=2, stop_length=1)
uart.send(b'Hello')
```