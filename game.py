from blessed import Terminal 
import random
import time
import Queue
import threading
import logging
import math
import datetime

def keyboard_input_worker(terminal, queue):
    t = terminal
    while True:
        with t.cbreak():
            # Wait for a key to be pressed, blocking indefinitely
            key = t.inkey(timeout=None)
            logging.info("keyboard: got key: {}".format((str(key), key.name, key.code)))
            if key.name != None:
                # Special keys e.g. left right etc. have a descriptive name like 'KEY_LEFT' # Normal keys like a,b,c don't have a key.name attribute
                queue.put(key.name)
            else:
                queue.put(str(key))


class Game:
    def __init__(self, score_needed_to_win=5):
        self.fps = 32
        self.score_needed_to_win = score_needed_to_win

        self.ball = Ball()
        self.paddle1 = Paddle("player1")
        self.paddle2 = Paddle("player2")
        self.user_interface = UserInterface(self.paddle1, self.paddle2)

        # Save a list of all game objects. This is useful for when they need to be iterated over.
        # Note the order of objects in the list also determines render order.
        self.game_objects = [self.user_interface, self.ball, self.paddle1, self.paddle2]

        self.keyboard_input_thread = None
        self.keyboard_input_queue  = None
        self.starting_next_round = False

    def init_keyboard_input_thread(self, terminal):
        # This queue is used for communication between the keyboard input thread and the main thread
        # When a key is pressed it is placed onto the queue
        # It is then popped off the queue in the main thread
        self.keyboard_input_queue = Queue.Queue(maxsize=1)
        self.keyboard_input_thread = threading.Thread(target=keyboard_input_worker, args=(terminal, self.keyboard_input_queue))

        # Setting the thread to a daemon means it will end when the main thread ends
        self.keyboard_input_thread.setDaemon(True)
        self.keyboard_input_thread.start()

    def play(self, terminal):
        self.init_keyboard_input_thread(terminal)

        with terminal.hidden_cursor(): # without this the terminal cursor flashes which looks bad
            self.reset_round(terminal)

            while True:
                # Time the duration of the frame and adjust the sleep duration accordingly.
                # This improves smoothness on the Pi.
                frame_start_time = datetime.datetime.now()

                # Note handle_input must come before update
                self.handle_input()
                self.update(terminal)
                self.redraw(terminal)

                frame_end_time = datetime.datetime.now()
                time_delta = (frame_end_time - frame_start_time).total_seconds()
                time.sleep(max(0, 1/float(self.fps) - time_delta))

                if self.starting_next_round:
                    self.next_round(terminal)

                #print terminal.clear

    def handle_input(self):
        try:
            key = self.keyboard_input_queue.get_nowait()

            if key == "w":
                self.paddle1.vy = -1
            elif key == "s":
                self.paddle1.vy = 1
            elif key == "o":
                self.paddle2.vy = -1
            elif key == "l":
                self.paddle2.vy = 1
            elif key == "p":
                # TODO: pause game
                pass
        except Queue.Empty:
            pass

    def draw(self, terminal):
        logging.info("game: Drawing")
        for object in self.game_objects:
            object.draw(terminal)

    def redraw(self, terminal):
        logging.info("game: Redrawing")
        for object in self.game_objects:
            object.redraw(terminal)

    def update(self, terminal):
        logging.info("game: Updating")
        for object in self.game_objects:
            object.update(terminal)

        # Perform collision detections
        # Firstly, check if ball hit walls
        b = self.ball # this is less verbose
        t = terminal
        y_min = self.user_interface.get_y_min()
        y_max = self.user_interface.get_y_max()

        if b.y <= y_min: 
            logging.info("game: Ball hit top of screen")
            b.y = y_min
            b.vy *= -1
        elif b.y >= y_max: 
            logging.info("game: Ball hit bottom of screen")
            b.y = y_max
            b.vy *= -1

        if b.x < 0: # player 1 missed
            logging.info("game: Player 2 scores")
            self.paddle2.score += 1
            self.starting_next_round = True
        elif b.x > t.width-1: # player 2 missed
            logging.info("game: Player 1 scores")
            self.paddle1.score += 1
            self.starting_next_round = True

        # Now check if ball hit paddles
        for paddle in [self.paddle1, self.paddle2]:
            if paddle.collides_with_ball(b):
                logging.info("game: Ball hit paddle")
                b.bounce_off_paddle(paddle)

        # Prevent the paddles moving off screen
        for paddle in [self.paddle1, self.paddle2]:
            if paddle.y < y_min:
                paddle.y = y_min
            elif paddle.y + paddle.height >= y_max:
                paddle.y = y_max - paddle.height

    def reset_round(self, terminal):
        logging.info("game: Resetting round")
        print terminal.clear
        for object in self.game_objects:
            object.reset(terminal)
            object.draw(terminal)

    def next_round(self, terminal):
        """
        Starts the next round after a point has been scored.
        """
        logging.info("game: Moving to next round")
        time.sleep(0.75)
        self.reset_round(terminal)
        self.starting_next_round = False

    def game_over(self):
        # TODO
        logging.info("game: Game over")
        # self.keyboard_input_thread.stop()
        print("GAME OVER!")
        pass

class Ball:
    def __init__(self):
        # Keep a note of the previous position to help when redrawing
        self.prev_x = None
        self.prev_y = None
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.init_speed = 0.5
        self.colour = "" 

    def reset(self, terminal):
        """
        Sets the ball's position to the middle of the screen.
        Also resets its velocity.
        """
        logging.debug("ball: Ball reset")
        self.colour = terminal.on_green

        self.prev_x = None
        self.prev_y = None
        self.x = terminal.width/2.0
        self.y = terminal.height/2.0

        # Choose starting direction randomly.
        # It could be either directly left or directly right
        rand_direction = random.choice([-1.0, 1.0])
        self.vx = rand_direction * self.init_speed
        self.vy = 0.0

    def draw(self, terminal):
        logging.debug("ball: Ball draw")
        terminal.draw_square(int(self.x), int(self.y), colour=self.colour)
    
    def redraw(self, terminal):
        logging.debug("ball: Ball redraw")
        # First remove the old ball
        terminal.draw_square(int(self.prev_x), int(self.prev_y))
        # Now draw the new one
        terminal.draw_square(int(self.x), int(self.y), colour=self.colour)

    def update(self, terminal):
        logging.debug("ball: Ball updated. x={0}, y={1}, vx={2}, vy={3}".format(self.x, self.y, self.vx, self.vy))
        self.prev_x = self.x
        self.prev_y = self.y

        self.x += self.vx
        self.y += self.vy

    def bounce_off_paddle(self, paddle):
        # Reverse the x direction
        if paddle.id == "player1":
            new_x_direction = 1
        else: # paddle.id == "player2"
            new_x_direction = -1

        # Randomize x velocity to +/- 0.5 of starting speed
        new_vx = (random.random() + 0.5) * self.init_speed

        y_delta = (self.y + 0.5) - (paddle.y + paddle.height/2.0)

        self.vx = new_x_direction * new_vx
        self.vy = (2 * y_delta * self.init_speed) / paddle.height

class Paddle:
    def __init__(self, id):
        # terminal should be a Blessed-library Terminal object
        # id should be either "player1" or "player2"
        self.id = id
        self.height = 5 # the height in terms of number of squares on the screen
        self.offset = 1 # how far from the sides of the screen the paddle should be
        self.speed = 0.2 # how quickly the paddle will move up or down
        self.score = 0 # score in points. 1 goal = 1 point

        self.prev_x = None
        self.prev_y = None
        self.y = 0 # the y position refers to the top of the paddle
        self.x = 0
        self.vy = 0.0 # velocity in the y direction

    def reset(self, terminal):
        """
        Resets the attributes of the paddle back to their defaults.
        Useful for repositioning after a goal.
        """
        if self.id == "player1":
            self.colour = terminal.on_blue
        else:
            self.colour = terminal.on_red

        self.height = 5
        self.speed = 0.2
        self.y = terminal.height / 2.0 - math.floor(self.height / 2.0)

        if self.id == "player1":
            self.x = self.offset
        else: # self.id == "player2"
            self.x = terminal.width - 1 - self.offset

        self.prev_x = None
        self.prev_y = None

        self.vy = 0

    def draw(self, terminal):
        # Draw each of the paddle's squares one by one from the top down
        for y in range(0, self.height):
            terminal.draw_square(int(self.x), int(self.y + y), colour=self.colour)

    def redraw(self, terminal):
        # Only redraw if the paddle moved
        if self.prev_x != self.x or self.prev_y != self.y:
            for y in range(0, self.height):
                terminal.draw_square(int(self.prev_x), int(self.prev_y + y))

            for y in range(0, self.height):
                terminal.draw_square(int(self.x), int(self.y + y), colour=self.colour)

    def update(self, terminal):
        self.prev_x = self.x
        self.prev_y = self.y

        self.y += self.vy
        self.vy = 0

    def collides_with_ball(self, ball):
        """
        Returns True if the paddle is colliding with the ball, False otherwise.
        The variables left_x, right_x, top_y, bottom_y below define a rectangle which is the hitbox of the paddle.
        The hitbox for each paddle extends 1 square in front of it, which makes for more accurate looking collisions.
        """
        top_y = int(self.y)
        bottom_y = top_y + self.height

        if self.id == "player1":
            left_x = self.x
            right_x = self.x + 2
        else: # self.id == "player2"
            left_x = self.x - 1
            right_x = self.x + 1

        if (ball.y >= top_y and
            ball.y <= bottom_y and
            ball.x >= left_x and
            ball.x <= right_x):
                return True
        else:
            return False

class UserInterface:
    def __init__(self, paddle1, paddle2):
        self.paddle1 = paddle1
        self.paddle2 = paddle2

        self.y_min = 2 # these values are changed during update
        self.y_max = 10

    def reset(self, terminal):
        pass

    def draw(self, terminal):
        logging.debug("UI: UI draw")
        # Line across top
        print terminal.normal
        with terminal.location(0, 1):
            print terminal.white + u"\u2500" * terminal.width

        # Line down middle:
        self.draw_centre_line(terminal)

        # Pong text:
        with terminal.location(terminal.width/2 - 2, 0):
            print terminal.yellow + "PONG"

        # Scores
        print terminal.normal
        with terminal.location(0,0):
            print terminal.blue + str(self.paddle1.score)

        with terminal.location(terminal.width - 1 - len(str(self.paddle2.score)), 0):
            print terminal.red + str(self.paddle2.score)

    def redraw(self, terminal):
        """
        Just redraw the centre line incase the ball passed over it.
        """
        logging.debug("UI: UI redraw")
        self.draw_centre_line(terminal)

    def draw_centre_line(self, terminal):
        print terminal.normal + terminal.white
        for y in range(2, terminal.height-1):
            if y % 2 != 0:
                # \u2502 is vertical line character
                with terminal.location(terminal.width/2, y):
                    print u"\u2502"

    def update(self, terminal):
        logging.debug("UI: UI update")
        self.y_min = 2
        self.y_max = terminal.height - 3

    def get_y_min(self):
        """
        Returns the lowest y value not occupied by a UI element, thus defining the field where the ball can bounce.
        """
        return self.y_min

    def get_y_max(self):
        """
        Returns the maximum y value not occupied by a UI element, thus defining the field where the ball can bounce.
        """
        return self.y_max
