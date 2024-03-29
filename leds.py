import RPi.GPIO as GPIO
import config
import logging
import time
import threading
if config.enable_pyglow:
    from PyGlow import PyGlow
    pyglow = PyGlow(brightness=config.pyglow_default_brightness)

led_io_ports = [5,6,12,13,16,19,20,26]
current_led_showing = None

def setup():
    logging.info("leds: setup called.")
    GPIO.setmode(GPIO.BCM) #use Broadcom GPIO names
    for port in led_io_ports:
        GPIO.setup(port, GPIO.OUT, initial=0)

def test():
    # flash each led for 0.5 secs
    """
    for port in led_io_ports:
        GPIO.output(port, 1)
        time.sleep(0.5)
        GPIO.output(port, 0)

    flash_pyglow()
    """
    play_pyglow_effect()

def flash_pyglow():
    global pyglow
    pyglow.all(brightness=160)
    time.sleep(0.3)
    pyglow.all(brightness=0)
    time.sleep(0.3)
    pyglow.all(brightness=160)
    time.sleep(0.3)
    pyglow.all(brightness=0)
    time.sleep(0.3)
    pyglow.all(brightness=160)
    time.sleep(0.3)
    pyglow.all(brightness=0)
    time.sleep(0.3)

def pyglow_effect_worker():
    global pyglow
    groups = [
            [1,7,13],
            [2,8,14],
            [3,9,15],
            [4,10,16],
            [5,11,17],
            [6,12,18],
            [5,11,17],
            [4,10,16],
            [3,9,15],
            [2,8,14],
            [1,7,13],
            ]
    for group in groups:
        pyglow.led(group, brightness=160)
        time.sleep(0.1)
        pyglow.led(group, brightness=0)

def play_pyglow_effect():
    worker = threading.Thread(target=pyglow_effect_worker)
    worker.setDaemon(True)
    worker.start()

def follow_ball(ball):
    min_x = config.paddle_offset + 1
    max_x = config.game_width - config.paddle_offset - 2
    ball_percent_progress = (ball.x-min_x) / (max_x-min_x)
    # When the ball passes the paddles it will exceed min_x/max_x
    if ball_percent_progress < 0.0:
        ball_percent_progress = 0.0
    elif ball_percent_progress > 1.0:
        ball_percent_progress = 1.0

    next_led = led_io_ports[int(ball_percent_progress * len(led_io_ports)) - 1]

    global current_led_showing
    if current_led_showing != None:
        GPIO.output(current_led_showing, 0)

    GPIO.output(next_led, 1)
    current_led_showing = next_led
    logging.debug("leds: Ball progress: {0}. Showing led {1}".format(ball_percent_progress, current_led_showing))

if __name__ == "__main__":
    setup()
    test()
    GPIO.cleanup()
