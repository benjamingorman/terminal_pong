import RPi.GPIO as GPIO
import time
import datetime
import threading
import config

frequencies = {
	"C3": 130.81,
 	"C#3": 138.59,
	"Db3": 138.59,
	"D3": 146.83,
 	"D#3": 155.56,
	"Eb3": 155.56,
	"E3": 164.81,
	"F3": 174.61,
 	"F#3": 185.00,
	"Gb3": 185.00,
	"G3": 196.00,
 	"G#3": 207.65,
	"Ab3": 207.65,
	"A3": 220.00,
 	"A#3": 233.08,
	"Bb3": 233.08,
	"B3": 246.94,
	"C4": 261.63,
 	"C#4": 277.18,
	"Db4": 277.18,
	"D4": 293.66,
 	"D#4": 311.13,
	"Eb4": 311.13,
	"E4": 329.63,
	"F4": 349.23,
 	"F#4": 369.99,
	"Gb4": 369.99,
	"G4": 392.00,
 	"G#4": 415.30,
	"Ab4": 415.30,
	"A4": 440.00,
 	"A#4": 466.16,
	"Bb4": 466.16,
	"B4": 493.88,
	"C5": 523.25,
 	"C#5": 554.37,
	"Db5": 554.37,
	"D5": 587.33,
 	"D#5": 622.25,
	"Eb5": 622.25,
	"E5": 659.25,
	"F5": 698.46,
 	"F#5": 739.99,
	"Gb5": 739.99,
	"G5": 783.99,
 	"G#5": 830.61,
	"Ab5": 830.61,
	"A5": 880.00,
 	"A#5": 932.33,
	"Bb5": 932.33,
	"B5": 987.77
}

TRANSPOSE_AMOUNT = -10
SPEED = 90.0

minim = 2.0 * (60/SPEED)
crotchet = 1.0 * (60/SPEED)
quaver = 0.5 * (60/SPEED)
semiquaver = 0.25 * (60/SPEED)

PITCH_WORKER_OUTPUT_PERIOD = 0
PITCH_WORKER_SHOULD_STOP = False
def pitch_worker():
    """
    When play song is called, this function will be run in a thread.
    It constantly outputs a frequency on the music output pin.
    The global value PITCH_WORKER_OUTPUT_PERIOD can be changed to alter the pitch being output.
    """
    music_pin = config.gpio_pin_music
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(music_pin, GPIO.OUT, initial=0)

    global PITCH_WORKER_OUTPUT_PERIOD, PITCH_WORKER_SHOULD_STOP
    try:
        while True:
            if PITCH_WORKER_OUTPUT_PERIOD == 0:
                continue
            elif PITCH_WORKER_SHOULD_STOP:
                break
            else:
                delay = PITCH_WORKER_OUTPUT_PERIOD / 2.0
                GPIO.output(music_pin, 1)
                time.sleep(delay)
                GPIO.output(music_pin, 0)
                time.sleep(delay)
    finally:
        GPIO.cleanup()

def transpose(pitchstring, semitones):
    pitch_table = {
            "C": 0,
            "C#": 1,
            "Db": 1,
            "D": 2,
            "D#": 3,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "Gb": 6,
            "G": 7,
            "G#": 8,
            "Ab": 8,
            "A": 9,
            "A#": 10,
            "Bb": 10,
            "B": 11
        }
    reverse_pitchtable = dict(zip(pitch_table.values(), pitch_table.keys()))

    octave = int(pitchstring[-1])
    note = pitchstring[:-1]
    index = pitch_table[note]

    octave += (index+semitones)/12
    new_index = (index+semitones) % 12

    new_pitchstring = reverse_pitchtable[new_index] + str(octave)
    return new_pitchstring

def play_song(song):
    """
    A song is a series of tuples (pitchstring, duration)
    """
    pitch_worker_thread = threading.Thread(target=pitch_worker)
    pitch_worker_thread.setDaemon(True)
    pitch_worker_thread.start()

    global PITCH_WORKER_OUTPUT_PERIOD, PITCH_WORKER_SHOULD_STOP
    PITCH_WORKER_OUTPUT_PERIOD = 0
    PITCH_WORKER_SHOULD_STOP = False

    for note in song:
        pitchstring = note[0]
        duration = note[1]

        PITCH_WORKER_OUTPUT_PERIOD = 1.0/frequencies[pitchstring]
        time.sleep(duration*0.75) # duration is in seconds
        PITCH_WORKER_OUTPUT_PERIOD = 0.0
        time.sleep(duration*0.25)

        print("sleeping for " + str(duration) + " seconds")

    PITCH_WORKER_SHOULD_STOP = True

scale = [
        ("C3", quaver),
        ("D3", quaver),
        ("E3", quaver),
        ("F3", quaver),
        ("G3", quaver),
        ("A3", quaver),
        ("B3", quaver),
        ("C4", quaver)
        ]

imperialmarch = [
	("G3", crotchet),
	("G3", crotchet),
	("G3", crotchet),
	("Eb3", quaver * 1.5),
	("Bb3", semiquaver),

	("G3", crotchet),
	("Eb3", quaver * 1.5),
	("Bb3", semiquaver),
	("G3", minim),

	("D4", crotchet),
	("D4", crotchet),
	("D4", crotchet),
	("Eb4", quaver * 1.5),
	("Bb3", semiquaver),

	("Gb3", crotchet),
	("Eb3", quaver * 1.5),
	("Bb3", semiquaver),
	("G3", minim),

	("G4", crotchet),
	("G3", quaver * 1.5),
	("G3", semiquaver),
	("G4", crotchet),
	("Gb4", quaver * 1.5),
	("F4", semiquaver),

	("E4", semiquaver),
	("D#4", semiquaver),
	("E4", quaver),
	("G#3", quaver),
	("C#4", crotchet),
	("C4", quaver * 1.5),
	("B3", semiquaver),

	("Bb3", semiquaver),
	("A3", semiquaver),
	("Bb3", quaver),
	("Eb3", quaver),
	("Gb3", crotchet),
	("Eb3", quaver * 1.5),
	("Bb3", semiquaver),

	("G3", crotchet),
	("Eb3", quaver * 1.5),
	("Bb3", semiquaver),
	("G3", minim)
    ]

ohwhenthesaints = [
        ("C4", quaver),
        ("E4", quaver),
        ("F4", quaver),
        ("G4", minim + quaver),

        ("C4", quaver),
        ("E4", quaver),
        ("F4", quaver),
        ("G4", minim + quaver),

        ("C4", quaver),
        ("E4", quaver),
        ("F4", quaver),

        ("G4", crotchet),
        ("E4", crotchet),
        ("C4", crotchet),
        ("E4", crotchet),
        ("D4", minim + quaver),

        ("D4", quaver),
        ("E4", quaver),
        ("D4", quaver),

        ("C4", crotchet + quaver),
        ("C4", quaver),
        ("E4", crotchet),
        ("G4", crotchet),
        ("G4", quaver),
        ("F4", minim),
        ("F4", quaver)	,
        ("E4", quaver),
        ("F4", quaver),
        
        ("G4", crotchet),
        ("E4", crotchet),
        ("C4", crotchet),
        ("D4", crotchet),

        ("C4", minim * 2)
        ]

def start_theme_music():
    global theme_music_thread
    theme_music_thread = threading.Thread(target=play_song, args=(imperialmarch,))
    theme_music_thread.setDaemon(True)
    theme_music_thread.start()

def stop_theme_music():
    SHOULD_STOP_MUSIC = True

if __name__ == "__main__":
    print("minim: " + str(minim))
    print("crotchet: " + str(crotchet))
    print("quaver: " + str(quaver))
    print("semiquaver: " + str(semiquaver))

    play_song(imperialmarch)
