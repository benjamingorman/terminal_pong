import RPi.GPIO as GPIO
import config

GPIO.setmode(GPIO.BCM) #use Broadcom GPIO names
led_io_ports = [5,6,12,13,16,19,20,26]
for port in led_io_ports:
    GPIO.setup(port, GPIO.out, initial=0)

current_led_showing = None

def test():
    # flash each led for 0.5 secs
    for port in led_io_ports:
        GPIO.output(port, 1)
        sleep(0.5)
        GPIO.output(port, 0)

def follow_ball(ball):
    ball_percent_progress = ball.x / float(config.game_width-1)
    next_led = int(ball_percent_progress * len(led_io_ports)) - 1

    if current_led_showing != None:
        GPIO.output(current_led_showing, 0)

    GPIO.output(next_led, 1)
    current_led_showing = next_led
    logging.debug("leds: Ball progress: {0}. Showing led {1}".format(ball_percent_progress, current_led_showing))
