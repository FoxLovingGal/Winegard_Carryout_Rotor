#Python program to control Winegard Carryout as an AZ/EL Rotor from Gpredict
#This version created by Addison Wolf
#Credit to Gabe Emerson / Saveitforparts 2024, Email: gabe@saveitforparts.com for creating much of the base

import serial
import socket 
import regex as re

#initialize some variables
current_az = 0.00  
current_el = 0.00
index = 0

#define "carryout" as the serial port device to interface with
carryout = serial.Serial(
	port='COM4',             
	baudrate = 115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)
	
print ('Carryout antenna connected on ', carryout.port)

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


#listen to local port for rotctld commands
listen_ip = '127.0.0.1'  #listen on localhost
listen_port = 4533     #pass this from command line in future?
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind((listen_ip, listen_port))
client_socket.listen(1)

print ('Listening for rotor commands on', listen_ip, ':', listen_port)
conn, addr = client_socket.accept()
print ('Connection from ',addr)


#Would be nice to get initial / resting position from Carryout firmware
#I have not found a way to do this, just live position while motors are running


#pass rotor commands to Carryout
while 1:
	data = conn.recv(100)  #get Gpredict's message
	if not data:
		continue
		
	cmd = data.decode("utf-8").strip().split(" ")   #grab the incoming command
	#print("Received: ",cmd)    #debugging, what did Gpredict send?
	
	if cmd[0] == "p":   #Gpredict is requesting current position
		response = "{}\n{}\n".format(current_az, current_el)
		#print(response)
		conn.send(response.encode('utf-8'))
		
	elif cmd[0] == "P":   #Gpredict is sending desired position
		target_az = float(cmd[1])
		current_az = target_az
		target_el = float(cmd[2])
		current_el = target_el
		print(' Move antenna to:', target_az, ' ', target_el, end="\r")

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
		conn.send(response.encode('utf-8'))
						
		carryout.write(bytes(b'q\r')) #go back to Carryout's root menu
		
		
	elif cmd[0] == "S": #Gpredict says to stop
		print('Gpredict disconnected, exiting') #Do we want to do something else with this?
		conn.close()
		carryout.close()
		exit()
	else:
		print('Exiting')
		conn.close()
		carryout.close()
		exit()





