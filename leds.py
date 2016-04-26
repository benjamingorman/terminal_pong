import RPi.GPIO as GPIO

led_io_ports = [5,6,12,13,16,19,20,26]

def run():
    # flash each led for 0.5 secs
    for port in led_io_ports:
        GPIO.setup(port, GPIO.out, initial=0)
        GPIO.output(port, 1)
        sleep(0.5)
        GPIO.output(port, 0)

