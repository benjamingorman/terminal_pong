# blessings is a library to handle terminal escape codes
# documentation for it at http://pythonhosted.org/blessings/
import blessed
import logging
import os
import config
import game

# Set up logging configuration. Logs will be sent to the file 'game.log'
logging.basicConfig(filename="game.log", filemode="w", level=logging.DEBUG)

# The force_styling attribute is needed so that escape codes remain intact if the output from the program is piped
terminal = blessed.Terminal(force_styling=True)

if __name__ == "__main__":
    print terminal.enter_fullscreen
    print terminal.clear

    logging.info("main: Starting game")
    game = game.Game(terminal, score_needed_to_win=10)
    game.play()
