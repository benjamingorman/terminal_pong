# blessings is a library to handle terminal escape codes
# documentation for it at http://pythonhosted.org/blessings/
from blessed import Terminal 
import time
import os
import random
import threading # see https://pymotw.com/2/threading/
import Queue
import math

keys_pressed = set(["a", "b"])

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

t = Terminal()
print t.enter_fullscreen

# This queue is used for communication between the keyboard input thread and the main thread
# When a key is pressed it is placed onto the queue
# It is then popped off the queue in the main thread
input_thread_queue = Queue.Queue(maxsize=1)

input_thread = threading.Thread(target=keyboard_input_worker, args=(t, input_thread_queue))
input_thread.setDaemon(True)
input_thread.start()

def play_game():
    game_fps = 60

    # position the ball in the middle of the screen initially
    ball_x = (t.width - 1)/2.0
    ball_y = (t.height - 1)/2.0

    # it's initial velocity will be moving straight right or left, chosen randomly 
    ball_init_speed = 0.5
    ball_init_direction = random.choice([-1.0, 1.0])
    ball_vx = ball_init_direction * ball_init_speed
    ball_vy = 0.0

    paddle_height = 5
    paddle_offset = 1 # how far from the sides of the screen each paddle should be
    paddle_speed = 0.2

    p1_y = t.height / 2.0 # the y position of the top of the paddle
    p2_y = t.height / 2.0

    p1_vy = 0.0
    p2_vy = 0.0

    p1_score = 0
    p2_score = 0
    score_needed_to_win = 5

    with t.hidden_cursor(): # without this the terminal cursor flashes which looks bad
	while True:
	    # DRAW
            # debug
            with t.location(0,0):
                print(" ".join(key for key in keys_pressed))
	    # ball
	    with t.location(int(ball_x), int(ball_y)):
		print t.on_green(" ")
	    
	    # paddles
	    p1_x = 0 + paddle_offset
	    p2_x = t.width - 1 - paddle_offset
	    for y in range(0, paddle_height):
		# p1:
		with t.location(p1_x, int(p1_y) + y):
		    print t.on_blue(" ")

		# p2:
		with t.location(p2_x, int(p2_y) + y):
		    print t.on_red(" ")

	    # Check for player input
            try:
                key = input_thread_queue.get_nowait()
                if key != None:
                    keys_pressed.add(key)

                if key == "w":
                    p1_y -= 1
                elif key == "s":
                    p1_y += 1
                elif key == "KEY_UP":
                    p2_y -= 1
                elif key == "KEY_DOWN":
                    p2_y += 1
                elif key == "p":
                    pause = True
            except Queue.Empty:
                pass

	    # UPDATE
	    ball_x += ball_vx
	    ball_y += ball_vy

	    if ball_y < 0: # ball hit top of screen
		ball_y = 0
		ball_vy *= -1
	    elif ball_y > t.height-1: # ball hit bottom of screen
		ball_y = t.height-1
		ball_vy *= -1

	    if ball_x < 0: # player 1 missed
		p2_score += 1

		ball_x = 0
		ball_vx *= -1
		
		# TODO: reset positions
                ball_x = t.width/2
                ball_y = t.height/2
	    elif ball_x > t.width-1: # p2 missed
		p1_score += 1

		ball_x = t.width - 1 
		ball_vx *= -1

                ball_x = t.width/2
                ball_y = t.height/2

            # Collide ball with paddles
            # p1
            with t.location(0,1):
                print("ball_x={0}, ball_y={1}, ball_vx={2}, ball_vy={3}".format(ball_x, ball_y, ball_vx, ball_vy))
            with t.location(0,2):
                print("player 1 score: {0}, player 2 score: {1}".format(p1_score, p2_score))

            if ball_x > p1_x and ball_x < p1_x + 2:
                if ball_y > p1_y and ball_y < p1_y + paddle_height:
                    ball_vx *= -1
                    y_delta = ball_y - (p1_y + paddle_height/2)
                    ball_vy = (2*y_delta*ball_init_speed)/paddle_height


            if ball_x < p2_x and ball_x > p2_x - 2:
                if ball_y > p2_y and ball_y < p2_y + paddle_height:
                    ball_vx *= -1
                    y_delta = ball_y - (p2_y + paddle_height/2)
                    ball_vy = (2*y_delta*ball_init_speed)/paddle_height

            p1_y += p1_vy
            p2_y += p2_vy

            # Prevent the paddles moving off screen
            y_min = 0
            y_max = t.height - 1 - paddle_height

            if p1_y < y_min:
                p1_y = y_min 
            elif p1_y > y_max:
                p1_y = y_max

            if p2_y < y_min:
                p2_y = y_min 
            elif p2_y > y_max:
                p2_y = y_max

	    time.sleep(1 / float(game_fps))
	    print t.clear

play_game()

#tk.quit()
