import os

def is_running_on_pi():
    return os.uname()[1] == "raspberrypi"

game_width = 80
game_height = 20
game_fps = 32
game_score_needed_to_win = 10
game_over_pause_time = 4.0
ball_init_speed = 0.5
ball_bounce_randomness = 0.5 # after a bounce the ball's new velocity will be +/- this value from init_speed
paddle_height = 3 # height in terms of number of squares on the screen
paddle_offset = 1 # offset from the edge of the screen in squares
paddle_speed = 0.6
paddle_max_stretches = 2 # How many times can the player stretch the paddle per game
paddle_stretch_duration = 15.0

# The maximum and minimum numbers that can be returned by the adc
adc_max_val = 4096
adc_min_val = 0
adc_updates_per_sec = 5

adc_using_p1_ldr = False # Whether an LDR is being used for the player1 controller
adc_ldr_max_val = 4096
adc_ldr_min_val = 2200

gpio_pin_p1_stretch = 4 # pins 4 and 18 are located on the back of the adc board
gpio_pin_p1_serve = 18 
gpio_pin_p2_stretch = 9 # pins 9 and 11 are located on the far right of the base board, just left of pin 10
gpio_pin_p2_serve = 11 
gpio_pin_music = 10

output_down_serial_cable = False
serial_baud_rate = 115200

enable_music = True
enable_leds = True
enable_pyglow = True

pyglow_default_brightness = 0

# These patterns detail how each number in the player scores should be drawn in pixel form
score_width = 3
score_height = 5
score_offset = 8 # offset in squares from net
score_y = 1 # y position of top row
score_patterns = {
        0: [1,1,1,
            1,0,1,
            1,0,1,
            1,0,1,
            1,1,1],
        1: [0,0,1,
            0,0,1,
            0,0,1,
            0,0,1,
            0,0,1],
        2: [0,1,0,
            1,0,1,
            0,0,1,
            0,1,0,
            1,1,1],
        3: [1,1,1,
            0,0,1,
            0,1,1,
            0,0,1,
            1,1,1],
        4: [1,0,1,
            1,0,1,
            1,1,1,
            0,0,1,
            0,0,1],
        5: [1,1,1,
            1,0,0,
            1,1,1,
            0,0,1,
            1,1,1],
        6: [1,1,1,
            1,0,0,
            1,1,1,
            1,0,1,
            1,1,1],
        7: [1,1,1,
            0,0,1,
            0,0,1,
            0,1,0,
            1,0,0],
        8: [1,1,1,
            1,0,1,
            1,1,1,
            1,0,1,
            1,1,1],
        9: [1,1,1,
            1,0,1,
            1,1,1,
            0,0,1,
            1,1,1]
        }
