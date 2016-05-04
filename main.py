# blessings is a library to handle terminal escape codes
# documentation for it at http://pythonhosted.org/blessings/
import blessed
import logging
import os
import config
import game

# Set up logging configuration. Logs will be sent to the file 'game.log'
logging.basicConfig(filename="game.log", filemode="w", level=logging.DEBUG)

serialPort = None
if config.is_running_on_pi() and config.output_down_serial_cable:
    import serial
    serialPort = serial.Serial("/dev/ttyAMA0", config.serial_baud_rate)
    if not serialPort.isOpen():
        serialPort.open()

# The force_styling attribute is needed so that escape codes remain intact if the output from the program is piped
terminal = blessed.Terminal(force_styling=True, stream=serialPort)

if __name__ == "__main__":
    with terminal.fullscreen():
        with terminal.hidden_cursor(): # without this the cursor flashes which looks bad
            terminal.stream.write(terminal.clear)

            logging.info("main: Starting game")
            game = game.Game(terminal)
            game.play()
