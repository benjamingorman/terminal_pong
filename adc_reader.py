import smbus
import time
import config
import logging
import threading

I2CADDR = 0x21
bus = smbus.SMBus(1)

last_read_player1_input = 0
last_read_player2_input = 0

def adc_reader_worker():
    """
    This function will be the target of a thread, and will run in the background to periodically read the adc.
    It updates the global variables last_read_player{1,2}_input
    """
    while True:
        global last_read_player1_input
        global last_read_player2_input

        # First write byte to read from Vin3 - player1 input channel
        try:
            bus.write_byte(I2CADDR, 0x40)
            last_read_player1_input = read_from_adc()
        except IOError:
            logging.warning("adc_reader: IOError when writing to bus. Setting last_read_player1_input to a default value instead.")
            last_read_player1_input = config.adc_max_val / 2

        # Now write to read from Vin4 - player2 input channel
        try:
            bus.write_byte(I2CADDR, 0x80)
            last_read_player2_input = read_from_adc()
        except IOError:
            logging.warning("adc_reader: IOError when writing to bus. Setting last_read_player2_input to a default value instead.")
            last_read_player2_input = config.adc_max_val / 2

        time.sleep(1 / float(config.adc_updates_per_sec))

def setup():
    """
    Starts a background thread which reads from the adc periodically.
    """
    adc_reader_thread = threading.Thread(target=adc_reader_worker)
    adc_reader_thread.setDaemon(True)
    adc_reader_thread.start()

def get_player1_input():
    logging.debug("get_player1_input: returning " + str(last_read_player1_input))
    return last_read_player1_input

def get_player2_input():
    logging.debug("get_player2_input: returning " + str(last_read_player2_input))
    return last_read_player2_input

def read_from_adc():
    try:
        # the data that comes in looks like
        # [X, 8 bits][Y, 4 bits][Z, 4 bits]
        # The 'value' we want is ZX
        data_read = bus.read_word_data(I2CADDR, 0x00)
        X = (data_read >> 8) & 0xff
        Y = (data_read >> 4) & 0xf
        Z = data_read & 0xf
        ZX = (Z << 8) | X

        """
        print("data_read:   ", bin(data_read)[2:].zfill(16))
        print("X:           ", bin(X)[2:].zfill(8))
        print("Y:           ", bin(Y)[2:].zfill(4))
        print("Z:           ", bin(Z)[2:].zfill(4))
        print("ZX:          ", bin(ZX)[2:].zfill(12))
        """
        return ZX
    except IOError:
        # If there was a glitch, just assume the value read is the max value / 2 (i.e. 2048)
        return config.adc_max_val / 2

def debug():
    # Continually reads from the ADC and prints what it gets

    while True:
        # First player1
        bus.write_byte(I2CADDR, 0x40)
        value = read_from_adc()
        print(value)
        print("")

        time.sleep(0.25)

        # Now player2
        bus.write_byte(I2CADDR, 0x80)
        value = read_from_adc()
        print(value)
        print("")

        time.sleep(0.25)
