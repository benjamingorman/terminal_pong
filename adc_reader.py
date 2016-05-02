import smbus
import time


I2CADDR = 0x21

bus = smbus.SMBus(1)

# Setup ADC
# Config to write to config register, convert on vin3

while True:
	time.sleep(0.25)
	
	bus.write_byte(I2CADDR, 0x40)
        data_read = bin(bus.read_word_data(I2CADDR, 0x00))[2:]
	data_reordered = data_read[8:16] + data_read[0:8]
	alert_bit = data_reordered[0]
	zero_bit  = data_reordered[1]
	channel_identifier = data_reordered[2:4]

	value = data_reordered[-1:3:-1]
	x = int(value, 2)

        print("data_read:          " + data_read + " (" + format(int(data_read, 2), '#04X') + ") " + str(len(data_read)) + " bits")
        print("data_reordered:     " + data_reordered + " (" + format(int(data_reordered, 2), '#04X') + ") " + str(len(data_reordered)) + " bits")

	print("alert_bit:          " + alert_bit)
	print("zero_bit:           " + zero_bit)
	print("channel_identifier: " + channel_identifier)
	print("value:              " + value)
	print("x =                 " + str(x))
	print("-----")
