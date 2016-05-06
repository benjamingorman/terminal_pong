import RPi.GPIO as GPIO  
import config
GPIO.setmode(GPIO.BCM)

# Use Player 1 serve
pin = config.gpio_pin_p1_serve

LogicalState = 0

# main loop
while True:
    # setup pin as input with pull-up
    GPIO.setup(pin, GPIO.IN)  

    # waiting for interrupt from button press
    GPIO.wait_for_edge(pin, GPIO.RISING)  
    print("switch pressed")
    LogicalState = 1
    sleep(0.2)

    GPIO.wait_for_edge(pin, GPIO.FALLING)
    print("switch released")
    LogicalState = 0
    sleep(0.2)
