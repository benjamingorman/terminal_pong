import RPi.GPIO as GPIO
import time
import datetime

TRANSPOSE_AMOUNT = -12
SPEED = 240.0

minim = 2.0 * (30000/SPEED)
crotchet = 1.0 * (30000/SPEED)
quaver = 0.5 * (30000/SPEED)
semiquaver = 0.25 * (30000/SPEED)

GPIO.setwarnings(False) #disable runtime warnings
GPIO.setmode(GPIO.BCM) #use Broadcom GPIO names
GPIO.setup(10, GPIO.OUT) #set pin 10 as output

def get_time():
	return datetime.datetime.now()

def get_time_difference_millis(t1, t2):
	delta = t2 - t1
	secs = delta.seconds
	micros = delta.microseconds
	result = 1000 * secs + micros / 1000000.0
	return result

def play_note(period=0.1, duration=500):
	start_time  = datetime.datetime.now()
	delay = period / 2.0

	while get_time_difference_millis(start_time, get_time()) < duration:	
		GPIO.output(10, True) #set pin 10 high
		time.sleep(delay) #wait 1/2 sec
		GPIO.output(10, False) #set pin 10 low
		time.sleep(delay) #wait 1/2 sec

def sleepm(millis):
	time.sleep(millis/1000.0)


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
	"C5": 423.25,
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


pitches = {}
for note, freq in frequencies.iteritems():
    pitches[note] = 1.0/freq

def p(note, duration):
    if TRANSPOSE_AMOUNT != 0:
        note = transpose(note, TRANSPOSE_AMOUNT)

    play, sleep = duration * 0.75, duration * 0.25
    play_note(pitches[note], play)
    sleepm(sleep)

def scale():
	for note in ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"]:
		p(note, semiquaver)

def imperialmarch():
	p("G4", crotchet)
	p("G4", crotchet)
	p("G4", crotchet)
	p("Eb4", quaver * 1.5)
	p("Bb4", semiquaver)

	p("G4", crotchet)
	p("Eb4", quaver * 1.5)
	p("Bb4", semiquaver)
	p("G4", minim)

	p("D5", crotchet)
	p("D5", crotchet)
	p("D5", crotchet)
	p("Eb5", quaver * 1.5)
	p("Bb4", semiquaver)

	p("Gb4", crotchet)
	p("Eb4", quaver * 1.5)
	p("Bb4", semiquaver)
	p("G4", minim)

	p("G5", crotchet)
	p("G4", quaver * 1.5)
	p("G4", semiquaver)
	p("G5", crotchet)
	p("Gb5", quaver * 1.5)
	p("F5", semiquaver)

	p("E5", semiquaver)
	p("D#5", semiquaver)
	p("E5", quaver)
	sleepm(quaver)
	p("G#4", quaver)
	p("C#5", crotchet)
	p("C5", quaver * 1.5)
	p("B4", semiquaver)

	p("Bb4", semiquaver)
	p("A4", semiquaver)
	p("Bb4", quaver)
	sleepm(quaver)
	p("Eb4", quaver)
	p("Gb4", crotchet)
	p("Eb4", quaver * 1.5)
	p("Bb4", semiquaver)

	p("G4", crotchet)
	p("Eb4", quaver * 1.5)
	p("Bb4", semiquaver)
	p("G4", minim)

def ohwhenthesaints():
	p("C4", quaver)
	p("E4", quaver)
	p("F4", quaver)
	p("G4", minim + quaver)

	p("C4", quaver)
	p("E4", quaver)
	p("F4", quaver)
	p("G4", minim + quaver)

	p("C4", quaver)
	p("E4", quaver)
	p("F4", quaver)

	p("G4", crotchet)
	p("E4", crotchet)
	p("C4", crotchet)
	p("E4", crotchet)
	p("D4", minim + quaver)

	p("D4", quaver)
	p("E4", quaver)
	p("D4", quaver)

	p("C4", crotchet + quaver)
	p("C4", quaver)
	p("E4", crotchet)
	p("G4", crotchet)
	p("G4", quaver)
	p("F4", minim)
	p("F4", quaver)	
	p("E4", quaver)
	p("F4", quaver)
	
	p("G4", crotchet)
	p("E4", crotchet)
	p("C4", crotchet)
	p("D4", crotchet)

	p("C4", minim * 2)

if __name__ == "__main__":
    #imperialmarch()
    #scale()
    ohwhenthesaints()
