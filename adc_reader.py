import smbus
import time


I2CADDR = 0x21

bus = smbus.SMBus(1)

while True:
	time.sleep(0.5)
	

	bus.write_byte( I2CADDR, 0x20 )

	tmp = bus.read_word_data( I2CADDR, 0x00 )
	x=none
	for a in range(4,16):
		x.append(temp[20-a])
	return (x)	
