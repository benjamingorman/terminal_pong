from blessed import Terminal 
import random
import time
import Queue
import threading
import logging
import math
import datetime
import config

if config.is_running_on_pi():
    import leds

# We keep a global reference to the terminal object
# This value is set when a Game is created.
terminal = None

# This function provides an interface for game objects to draw squares to the screen.
# It allows for some optimizations - for example if the same colour square is to be drawn more than once, the colour escape code will be sent only once.
previous_square_colour = None
def draw_square(x, y, colour=""):
    if terminal == None:
        raise RuntimeError("draw_square called but terminal has not been set. Have you created a Game object yet?")

    terminal.stream.write(terminal.move(int(y), int(x)))
    
    try:
        terminal.stream.flush()
    except Exception:
        logging.error("Terminal could not flush stream!")

    # Check to see if the new colour is different to the last colour.
    # This minimizes the number of colour changes needed.
    global previous_square_colour
    if previous_square_colour != colour:
        if colour == "":
            print(terminal.normal + " ")
        else:
            print(colour + " ")

        previous_square_colour = colour
    else:
        print(" ")

# This function is used only when running on a PC (not on the Pi) and allows the game to be played with keyboard input.
# It will be ran in a seperate thread when the game is started.
def keyboard_input_worker(queue):
    while True:
        with terminal.cbreak():
            # Wait for a key to be pressed, blocking indefinitely
            key = terminal.inkey(timeout=None)
            logging.info("keyboard: got key: {}".format((str(key), key.name, key.code)))
            if key.name != None:
                # Special keys e.g. left right etc. have a descriptive name like 'KEY_LEFT' # Normal keys like a,b,c don't have a key.name attribute
                queue.put(key.name)
            else:
                queue.put(str(key))


class Game:
    def __init__(self, term, score_needed_to_win=10):
        # term is a blessed.Terminal object
        # set the global variable terminal for ease of access
        global terminal
        terminal = term
        self.score_needed_to_win = score_needed_to_win

        self.width = config.game_width
        self.height = config.game_height
        self.fps = config.game_fps

        self.ball = Ball()
        self.paddle1 = Paddle("player1")
        self.paddle2 = Paddle("player2")
        self.user_interface = UserInterface(self.ball, self.paddle1, self.paddle2)

        # Save a list of all game objects. This is useful for when they need to be iterated over.
        # Note the order of objects in the list also determines render order.
        self.game_objects = [self.ball, self.paddle1, self.paddle2, self.user_interface]

        self.keyboard_input_thread = None
        self.keyboard_input_queue  = None
        self.starting_next_round = False

        # Keep a reference to the terminal's width and height and clear/refresh the display if it changes.
        # This helps to prevent display errors.
        self.prev_terminal_width = terminal.width
        self.prev_terminal_height = terminal.height


    def init_keyboard_input_thread(self):
        # This queue is used for communication between the keyboard input thread and the main thread
        # When a key is pressed it is placed onto the queue
        # It is then popped off the queue in the main thread
        self.keyboard_input_queue = Queue.Queue(maxsize=1)
        self.keyboard_input_thread = threading.Thread(target=keyboard_input_worker, args=(self.keyboard_input_queue,))

        # Setting the thread to a daemon means it will end when the main thread ends
        self.keyboard_input_thread.setDaemon(True)
        self.keyboard_input_thread.start()

    def play(self):
        if not config.is_running_on_pi():
            logging.debug("Initializing keyboard input thread since we're not on the Pi.")
            self.init_keyboard_input_thread()
        else:
            logging.debug("On the Pi so not using keyboard input.")

        with terminal.hidden_cursor(): # without this the terminal cursor flashes which looks bad
            self.reset_round()

            while True:
                # Time the duration of the frame and adjust the sleep duration accordingly.
                # This improves fps accuracy on the Pi.
                frame_start_time = datetime.datetime.now()

                # Note handle_input must come before update
                self.handle_input()
                self.update()

                if terminal.width != self.prev_terminal_width or terminal.height != self.prev_terminal_height:
                    logging.info("Terminal resized so clearing screen.")
                    print terminal.normal + terminal.clear 
                    self.prev_terminal_width = terminal.width
                    self.prev_terminal_height = terminal.height
                    self.draw()
                else:
                    self.redraw()

                frame_end_time = datetime.datetime.now()
                time_delta = (frame_end_time - frame_start_time).total_seconds()
                time_to_sleep = max(0, 1/float(self.fps) - time_delta)
                time.sleep(time_to_sleep)
                logging.debug("time delta: {0}, sleep time: {1}".format(time_delta, time_to_sleep))

                if self.starting_next_round:
                    self.next_round()

                # The screen should not need to be cleared since every game object's redraw method should clear it's last position 
                #print terminal.clear

    def handle_input(self):
        if config.is_running_on_pi():
            # TODO: Change this
            logging.debug("Running on Pi so not handling input.")
            return

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
            # If no keys have been pressed the queue will be empty and this exception will be raised.
            # It's not a problem so just continue.
            pass

    def draw(self):
        """
        The point of draw is to have each game object draw itself to the screen.
        It is only called on the first frame of each round, or if the terminal has been resized. Aside from these special cases, redraw is always used.
        The point of this is that redraw cares about erasing the game object's previous position, but draw does not - it simply draws the object.
        """
        logging.info("game: Drawing")
        for object in self.game_objects:
            object.draw()

    def redraw(self):
        """
        The point of redraw is to have each game object erase it's last position and then draw it's new position.
        This prevents the screen from having to be completely cleared every frame and thus makes the game render more smoothly.
        """
        logging.info("game: Redrawing")
        for object in self.game_objects:
            object.redraw()

    def update(self):
        """
        Updates all the game objects and then performs collision detection.
        """
        logging.info("game: Updating")
        for object in self.game_objects:
            object.update()

        if config.is_running_on_pi():
            leds.follow_ball(self.ball)

        # Perform collision detections
        # Firstly, check if ball hit walls
        b = self.ball # this is less verbose
        t = terminal
        y_min = 0
        y_max = config.game_height - 1

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
        elif b.x > self.width-1: # player 2 missed
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

    def reset_round(self):
        logging.info("game: Resetting round")
        print terminal.normal + terminal.clear
        for object in self.game_objects:
            object.reset()
            object.draw()

    def next_round(self):
        """
        Starts the next round after a point has been scored.
        """
        logging.info("game: Moving to next round")
        time.sleep(0.75)
        self.reset_round()
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
        self.vx = 0 # velocity in x and y directions
        self.vy = 0
        self.init_speed = config.ball_init_speed 
        self.colour = terminal.on_green

    def reset(self):
        """
        Sets the ball's position to the middle of the screen.
        Also resets its velocity.
        """
        logging.debug("ball: Ball reset")

        self.prev_x = None
        self.prev_y = None
        self.x = config.game_width/2.0
        self.y = config.game_height/2.0

        # Choose starting direction randomly.
        # It could be either directly left or directly right
        rand_direction = random.choice([-1.0, 1.0])
        self.vx = rand_direction * self.init_speed
        self.vy = 0.0

    def draw(self):
        logging.debug("ball: Ball draw")
        draw_square(int(self.x), int(self.y), colour=self.colour)
    
    def redraw(self):
        logging.debug("ball: Ball redraw")
        # First remove the old ball
        draw_square(int(self.prev_x), int(self.prev_y))

        # Now draw the new one
        draw_square(int(self.x), int(self.y), colour=self.colour)

    def update(self):
        self.prev_x = self.x
        self.prev_y = self.y

        self.x += self.vx
        self.y += self.vy
        logging.debug("ball: Ball updated. prev_x={0}, prev_y={1}, x={2}, y={3}, vx={4}, vy={5}".format(self.prev_x, self.prev_y, self.x, self.y, self.vx, self.vy))
        if self.prev_x == config.game_width/2:
            logging.debug("ball: Ball prev_x is 40. Maybe it hit net!?")

    def bounce_off_paddle(self, paddle):
        # Reverse the x direction
        if paddle.id == "player1":
            new_x_direction = 1
        else: # paddle.id == "player2"
            new_x_direction = -1

        # Randomize x velocity
        # The config value ball_bounce_randomness is used to determine the range of speeds the ball can attain
        r = config.ball_bounce_randomness
        new_vx = (1.0 - r + random.random() * 2 * r) * self.init_speed

        y_delta = (self.y + 0.5) - (paddle.y + paddle.height/2.0)

        self.vx = new_x_direction * new_vx
        self.vy = (2 * y_delta * self.init_speed) / paddle.height

class Paddle:
    def __init__(self, id):
        # terminal should be a Blessed-library Terminal object
        # id should be either "player1" or "player2"
        self.id = id
        self.height = config.paddle_height
        self.offset = config.paddle_offset 
        self.speed = config.paddle_speed
        self.score = 0 # score in points. 1 goal = 1 point

        self.prev_x = None
        self.prev_y = None
        self.y = 0 # the y position refers to the top of the paddle
        self.x = 0
        self.vy = 0.0 # velocity in the y direction
        if self.id == "player1":
            self.colour = terminal.on_blue
        else:
            self.colour = terminal.on_red


    def reset(self):
        """
        Resets the attributes of the paddle back to their defaults.
        Useful for repositioning after a goal.
        """
        self.height = config.paddle_height 
        self.speed = config.paddle_speed
        self.y = config.game_height / 2.0 - math.floor(self.height / 2.0)

        if self.id == "player1":
            self.x = self.offset
        else: # self.id == "player2"
            self.x = config.game_width - 1 - self.offset

        self.prev_x = None
        self.prev_y = None

        self.vy = 0

    def draw(self):
        # Draw each of the paddle's squares one by one from the top down
        for i in range(0, self.height):
            draw_square(int(self.x), int(self.y + i), colour=self.colour)

    def redraw(self):
        # Only redraw if the paddle moved
        if self.prev_x != self.x or self.prev_y != self.y:
            for y in range(0, self.height):
                draw_square(int(self.prev_x), int(self.prev_y + y))

            for y in range(0, self.height):
                draw_square(int(self.x), int(self.y + y), colour=self.colour)

    def update(self):
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
    def __init__(self, ball, paddle1, paddle2):
        # Keep a reference to the ball so we can tell if it passed over the UI or not
        self.ball = ball

        self.paddle1 = paddle1
        self.paddle2 = paddle2

        # The set of square co-ordinates making up the net
        self.net_positions = set()
        self.calc_net_positions()

        # The set of square co-ordinates making up each player's score
        self.p1_score_positions = set()
        self.p2_score_positions = set()
        self.calc_score_positions()

    def reset(self):
        self.calc_net_positions()
        self.calc_score_positions()

    def calc_net_positions(self):
        self.net_positions = set()
        net_x = config.game_width/2
        for y in range(2, config.game_height):
            if (y-2) % 4 == 0 or (y-3) % 4 == 0:
                self.net_positions.add((net_x, y))

    def calc_score_positions(self):
        for player in [self.paddle1, self.paddle2]:
            score_len = len(str(player.score))

            if player.id == "player1":
                score_start_x = config.game_width/2 - config.score_offset - score_len * config.score_width + (score_len - 1)
            else:
                score_start_x = config.game_width/2 + config.score_offset

            positions = set()
            for i, num in enumerate(str(player.score)):
                num_x = score_start_x + i * (config.score_width + 1)
                num_y = config.score_y

                for j, val in enumerate(config.score_patterns[int(num)]):
                    if val == 1:
                        x = num_x + j % config.score_width 
                        y = num_y + j / config.score_width
                        positions.add((x,y))

            if player.id == "player1":
                self.p1_score_positions = positions
            else:
                self.p2_score_positions = positions

    def draw(self):
        """
        Draws the net down the middle and the scores for each player.
        """
        logging.debug("UI: UI draw")

        # Draw net 
        for x,y in self.net_positions:
            draw_square(x, y, colour=terminal.on_white)

        # Draw scores
        # Player 1
        for x,y in self.p1_score_positions:
            draw_square(x, y, colour=self.paddle1.colour)

        # Player 2
        for x,y in self.p2_score_positions:
            draw_square(x, y, colour=self.paddle2.colour)


    def redraw(self):
        """
        Detect if the ball passed over a square in the UI and if so then redraw it.
        """
        prev_x = int(self.ball.prev_x)
        prev_y = int(self.ball.prev_y)

        if (prev_x, prev_y) in self.net_positions:
            logging.debug("Ball passed over net so redrawing the square.")
            draw_square(prev_x, prev_y, colour=terminal.on_white)
        elif (prev_x, prev_y) in self.p1_score_positions:
            logging.debug("Ball passed over p1 score so redrawing the square.")
            draw_square(prev_x, prev_y, colour=self.paddle1.colour)
        elif (prev_x, prev_y) in self.p2_score_positions:
            logging.debug("Ball passed over p2 score so redrawing the square.")
            draw_square(prev_x, prev_y, colour = self.paddle2.colour)

    def update(self):
        logging.debug("UI: UI update")
