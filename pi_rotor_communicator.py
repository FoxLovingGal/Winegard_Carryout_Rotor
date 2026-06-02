import serial
import regex as re
import sys


def timeout():
	print("did not receive input after starting, closing program...")
	sys.exit()


#initialize some variables
current_az = 0.00  
current_el = 0.00


#define "carryout" as the serial port device to interface with note we're def gonna need to change the port for the raspberry pi,
carryout = serial.Serial(
	port='/dev/ttyUSB0',             
	baudrate = 115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)



carryout.write(bytes(b'q\r')) #go back to root menu in case firmware was left in a submenu
carryout.write(bytes(b'\r')) #clear firmware prompt to avoid unknown command errors

#opens up motor menu and homes the motors, this way we will not have to manually open it up every time we want to use it
carryout.write(bytes(b'mot\r')) 
carryout.write(bytes(b'h *\r'))
finished = ''
reading = ''
#keeps code in this while loop until the home command is done, 
while not finished:
    reading = carryout.read(100).decode().strip()
    finished = re.search(r"MOT>$", reading)

carryout.write(bytes(b'q\r'))
print("Ready")



while 1:
	data = input()  #get Gpredict's message
	if not data:
		continue
		
	cmd = data.decode("utf-8").strip().split(" ")   #grab the incoming command
	#print("Received: ",cmd)    #debugging
	
	if cmd[0] == "p":   #Gpredict is requesting current position
		continue
		
	elif cmd[0] == "P":   #Gpredict is sending desired position
		target_az = float(cmd[1])
		current_az = target_az
		target_el = float(cmd[2])
		current_el = target_el

		while carryout.in_waiting != 0:
			carryout.read(100)

		
		
		#tell Carryout to move to target position
		carryout.write(bytes(b'mot\r'))

		az_command = ('a 0 ' + str(target_az) + '\r').encode('ascii')
		carryout.write(az_command)

		reply = carryout.read(100).decode().strip()
		#print('This is the reply for azimuth: ', reply)
		match = re.search('= (\\d+\\.\\d+)', reply)
		current_az = match.group(1).strip()

		while carryout.in_waiting != 0:
			carryout.read(100)

		el_command = ('a 1 ' + str(target_el) + '\r').encode('ascii')
		carryout.write(el_command)

		reply = carryout.read(100).decode().strip()
		#print('This is the reply for elevation: ', reply)
		match = re.search('= (\\d+\\.\\d+)', reply)
		current_el = match.group(1).strip()
			
		#Tell Gpredict things went correctly
		response="RPRT 0\n"  #Everything's under control, situation normal 
		print(response.encode('utf-8'))
						
		carryout.write(bytes(b'q\r')) #go back to Carryout's root menu
		
		
	elif cmd[0] == "S": #Gpredict says to stop
		sys.exit()
	else:
		sys.exit()