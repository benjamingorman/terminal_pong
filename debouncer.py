import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)  (could use GPIO.Board aswell though)

# use button x
gpio =   (pick which GPIO pin is used for button signal input)


LogicalState = 0

# main loop
while True:

    # setup GPIO "gpio" as input with pull-up
    GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

    # waiting for interrupt from button press
    GPIO.wait_for_edge(gpio, GPIO.FALLING)  

    # waiting for button release
    while (GPIO.input(gpio) == GPIO.LOW):

        # delay for debouncing-can alter delay depending on research
        sleep(0.2)
        
        
    # button released: toggle state
    if (LogicalState == 0):
        LogicalStatetate = 1
        system("/home/pi/io/led0 1900 100")
        # switch on
    else:
        LogicalState = 0
        # switch off

    GPIO.cleanup()
