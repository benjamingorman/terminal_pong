import smbus
import time
import config
import logging
import threading
import RPi.GPIO as GPIO

I2CADDR = 0x21
bus = smbus.SMBus(1)

last_read_player1_input = {
        "movement":0, # set by resistor input on adc
        "stretch":0,  # set by push switch
        "serve":0     # set by push switch
        }
last_read_player2_input = {
        "movement":0,
        "stretch":0, 
        "serve":0    
        }



def input_reader_worker():
    """
    This function will be the target of a thread, and will run in the background to periodically read the adc.
    It updates the global variables last_read_player{1,2}_input
    """
    while True:
        global last_read_player1_input
        global last_read_player2_input

        # First read movement inputs from adc
        # First write byte to read from Vin3 - player1 input channel
        try:
            bus.write_byte(I2CADDR, 0x80)
            last_read_player1_input["movement"] = read_from_adc()
        except IOError:
            logging.warning("hardware_input: IOError when writing to bus. Setting last_read_player1_input to a default value instead.")
            last_read_player1_input["movement"] = config.adc_max_val / 2

        # Now write to read from Vin4 - player2 input channel
        try:
            bus.write_byte(I2CADDR, 0x40)
            last_read_player2_input["movement"] = read_from_adc()
        except IOError:
            logging.warning("hardware_input: IOError when writing to bus. Setting last_read_player2_input to a default value instead.")
            last_read_player2_input["movement"] = config.adc_max_val / 2

        # Then read switch inputs from GPIO ports
        try:
            last_read_player1_input["stretch"] = GPIO.input(config.gpio_pin_p1_stretch)
            last_read_player1_input["serve"] = GPIO.input(config.gpio_pin_p1_serve)
        except IOError:
            logging.warning("hardware_input: Unable to read player1 switch input")

        try:
            last_read_player2_input["stretch"] = GPIO.input(config.gpio_pin_p2_stretch)
            last_read_player2_input["serve"] = GPIO.input(config.gpio_pin_p2_serve)
        except IOError:
            logging.warning("hardware_input: Unable to read player2 switch input")

        time.sleep(1 / float(config.adc_updates_per_sec))

def setup():
    """
    Starts a background thread which reads from the adc periodically.
    Also configures neccessary switch GPIO pins.
    """
    GPIO.setmode(GPIO.BCM)
    for pin in [config.gpio_pin_p1_stretch,
                config.gpio_pin_p1_serve,
                config.gpio_pin_p2_stretch,
                config.gpio_pin_p2_serve]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    input_reader_thread = threading.Thread(target=input_reader_worker)
    input_reader_thread.setDaemon(True)
    input_reader_thread.start()

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

def debug(player1=True, player2=True):
    GPIO.setmode(GPIO.BCM)
    for pin in [config.gpio_pin_p1_stretch,
                config.gpio_pin_p1_serve,
                config.gpio_pin_p2_stretch,
                config.gpio_pin_p2_serve]:
        GPIO.setup(pin, GPIO.IN)
    # Continually reads from the ADC and prints what it gets

    while True:
        # First player1
        if player1:
            print("player1:")
            bus.write_byte(I2CADDR, 0x80)
            movement_value = read_from_adc()
            stretch_value = GPIO.input(config.gpio_pin_p1_stretch)
            serve_value = GPIO.input(config.gpio_pin_p1_serve)
            print("movement: {0}, stretch: {1}, serve: {2}".format(movement_value, stretch_value, serve_value))

            print("")
            time.sleep(0.25)

        if player2:
            # Now player2
            print("player2:")
            bus.write_byte(I2CADDR, 0x40)
            movement_value = read_from_adc()
            stretch_value = GPIO.input(config.gpio_pin_p2_stretch)
            serve_value = GPIO.input(config.gpio_pin_p2_serve)
            print("movement: {0}, stretch: {1}, serve: {2}".format(movement_value, stretch_value, serve_value))
            print("")

            time.sleep(0.25)
