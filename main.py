# blessings is a library to handle terminal escape codes
# documentation for it at http://pythonhosted.org/blessings/
from blessed import Terminal 
import game
import logging

logging.basicConfig(filename="game.log", filemode="w", level=logging.DEBUG)

t = Terminal()
print t.enter_fullscreen

game = game.Game(t, score_needed_to_win=5)
logging.info("main: Starting game")
game.play()
