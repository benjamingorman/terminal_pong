from blessed import Terminal 
import random
import time
import Queue
import threading
import logging

def keyboard_input_worker(terminal, queue):
    t = terminal
    while True:
        with t.cbreak():
            # Wait for a key to be pressed, blocking indefinitely
            key = t.inkey(timeout=None)
            with t.location(0,1):
                pass
                #print("got key: {}".format((str(key), key.name, key.code)))
            if key.name != None:
                # Special keys e.g. left right etc. have a descriptive name like 'KEY_LEFT'
                # Normal keys like a,b,c don't have a key.name attribute
                queue.put(key.name)
            else:
                queue.put(str(key))


class Game:
    def __init__(self, terminal, score_needed_to_win=5):
        # terminal argument should be a Blessed-library Terminal object
        self.terminal = terminal
        self.fps = 32
        self.score_needed_to_win = score_needed_to_win

        self.ball = Ball(terminal)
        self.paddle1 = Paddle(terminal, "player1")
        self.paddle2 = Paddle(terminal, "player2")

        #self.keyboard_input_thread = None
        #self.keyboard_input_queue  = None
        #self.init_keyboard_input_thread()

    def init_keyboard_input_thread(self):
        # This queue is used for communication between the keyboard input thread and the main thread
        # When a key is pressed it is placed onto the queue
        # It is then popped off the queue in the main thread
        self.keyboard_input_queue = Queue.Queue(maxsize=1)
        self.keyboard_input_thread = threading.Thread(target=keyboard_input_worker, args=(self.terminal, self.keyboard_input_queue))
        self.keyboard_input_thread.setDaemon(True)
        self.keyboard_input_thread.start()

    def play(self):
        self.reset_round() # move all objects to their default positions

        with self.terminal.hidden_cursor(): # without this the terminal cursor flashes which looks bad
            while True:
                self.draw()
                #self.handle_input()
                self.update()

                time.sleep(1 / float(self.fps))
                
                #self.undraw()
                print self.terminal.clear

    def handle_input(self):
        try:
            key = self.keyboard_input_queue.get_nowait()

            if key == "w":
                self.paddle1.y -= 1
            elif key == "s":
                self.paddle1.y += 1
            elif key == "KEY_UP":
                self.paddle2.y -= 1
            elif key == "KEY_DOWN":
                self.paddle2.y += 1
            elif key == "p":
                # TODO: pause game
                pass
        except Queue.Empty:
            pass

    def draw(self):
        logging.info("game: Drawing")
        for object in [self.ball]: #[self.ball, self.paddle1, self.paddle2]:
            object.draw()
    
    def undraw(self):
        logging.info("game: Undrawing")
        for object in [self.ball]: #[self.ball, self.paddle1, self.paddle2]:
            object.undraw()

    def update(self):
        logging.info("game: Updating")
        for object in [self.ball]: #[self.ball, self.paddle1, self.paddle2]:
            object.update()

        # Perform collision detections
        # Firstly, check if ball hit walls
        b = self.ball # this is less verbose
        t = self.terminal
        if b.y < 0: 
            logging.info("game: Ball hit top of screen")
            b.y = 0.0
            b.vy *= -1
        elif b.y > t.height-1:
            logging.info("game: Ball hit bottom of screen")
            b.y = self.terminal.height-1
            b.vy *= -1

        if b.x < 0: # player 1 missed
            logging.info("game: Player 2 scores")
            self.paddle2.score += 1
            self.reset_round()
        elif b.x > t.width-1: # player 2 missed
            logging.info("game: Player 1 scores")
            self.paddle1.score += 1
            self.reset_round()

        # Now check if ball hit paddles
        for paddle in [self.paddle1, self.paddle2]:
            if paddle.collides_with_ball(b):
                logging.info("game: Ball hit paddle")
                y_delta = b.y - (paddle.y + paddle.height/2.0)

                b.vx *= -1
                b.vy = (2 * y_delta * b.init_speed) / paddle.height

    def reset_round(self):
        logging.info("game: Resetting round")
        for object in [self.ball, self.paddle1, self.paddle2]:
            object.reset()

    def game_over(self):
        # TODO
        logging.info("game: Game over")
        # self.keyboard_input_thread.stop()
        print("GAME OVER!")
        pass

class Ball:
    def __init__(self, terminal):
        self.terminal = terminal
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.init_speed = 0.5
        self.colour = terminal.on_green
        self.reset()

    def reset(self):
        """
        Sets the ball's position to the middle of the screen.
        Also resets its velocity.
        """
        self.x = (self.terminal.width - 1)/2.0
        self.y = (self.terminal.height - 1)/2.0

        # Choose starting direction randomly.
        # It could be either directly left or directly right
        rand_direction = random.choice([-1.0, 1.0])
        self.vx = rand_direction * self.init_speed
        self.vy = 0.0

    def draw(self):
        self.terminal.move(int(self.y), int(self.x))
        print(self.colour + " ")

    def undraw(self):
        self.terminal.move(int(self.y), int(self.x))
        print(" ")

    def update(self):
        logging.debug("ball: Ball updated. x={0}, y={1}, vx={2}, vy={3}".format(self.x, self.y, self.vx, self.vy))
        self.x += self.vy
        self.y += self.vy

class Paddle:
    def __init__(self, terminal, id):
        # terminal should be a Blessed-library Terminal object
        # id should be either "player1" or "player2"
        self.terminal = terminal
        self.id = id
        self.height = 5 # the height in terms of number of squares on the screen
        self.offset = 1 # how far from the sides of the screen the paddle should be
        self.speed = 0.2 # how quickly the paddle will move up or down
        self.score = 0 # score in points. 1 goal = 1 point
        self.y = 0 # the y position refers to the top of the paddle
        self.x = 0
        self.vy = 0.0 # velocity in the y direction

        if self.id == "player1":
            self.colour = terminal.on_blue
        else:
            self.colour = terminal.on_red

        self.reset()

    def reset(self):
        """
        Resets the attributes of the paddle back to their defaults.
        Useful for repositioning after a goal.
        """
        self.height = 5
        self.speed = 0.2
        self.y = self.terminal.height / 2.0 - self.height / 2.0

        if self.id == "player1":
            self.x = self.offset
        else: # self.id == "player2"
            self.x = self.terminal.width - 1 - self.offset

        self.vy = 0

    def draw(self):
        # Draw each of the paddle's squares one by one from the top down
        for y in range(0, self.height):
            self.terminal.move(int(self.y) + y, self.x)
            print(self.colour + " ")

    def undraw(self):
        # Does the opposite of draw, i.e. erases the paddle from the screen
        for y in range(0, self.height):
            self.terminal.move(int(self.y) + y, self.x)
            print(" ")

    def update(self):
        self.y += self.vy

        # Prevent the paddles moving off screen
        y_min = 0
        y_max = self.terminal.height - 1 - self.height

        if self.y < y_min:
            self.y = y_min
        elif self.y > y_max:
            self.y = y_max

    def collides_with_ball(self, ball):
        if ball.y > self.y and ball.y < self.y + self.height:
            if ball.x > self.x and ball.x < self.x + 1:
                return True
        else:
            return False
