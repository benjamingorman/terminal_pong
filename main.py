# blessings is a library to handle terminal escape codes
# documentation for it at http://pythonhosted.org/blessings/
import blessed
import game
import logging
import os

def is_running_on_pi():
    return os.uname()[1] == "raspberrypi"

if is_running_on_pi():
    import leds

# Set up logging configuration. Logs will be sent to the file 'game.log'
logging.basicConfig(filename="game.log", filemode="w", level=logging.DEBUG)

# We override Blessed's default Terminal class to add the draw_square function, allowing our game objects to draw to the screen.
# This interface helps to decouple our code from the Blessed code.
class PongTerminal(blessed.Terminal):
    def draw_square(self, x, y, colour=""):
        self.stream.write(self.move(int(y), int(x)))
        
        try:
            self.stream.flush()
        except e:
            logging.error("Terminal could not flush stream!")

        # Check to see if the new colour is different to the last colour.
        # This minimizes the number of colour changes needed.
        if self.previous_square_colour != colour:
            if colour == "":
                print(self.normal + " ")
            else:
                print(colour + " ")

            self.previous_square_colour = colour
        else:
            print(" ")

if __name__ == "__main__":
    t = PongTerminal(force_styling=True)
    print t.enter_fullscreen
    print t.clear

    logging.info("main: Starting game")
    game = game.Game(t, score_needed_to_win=5)
    game.play()
