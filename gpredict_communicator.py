#Python program to control Winegard Carryout as an AZ/EL Rotor from Gpredict
#This version created by Addison Wolf
#Credit to Gabe Emerson / Saveitforparts 2024, Email: gabe@saveitforparts.com for creating much of the base

import paramiko
import socket 
import regex as re
import getpass

#initialize some variables
current_az = 0.00  
current_el = 0.00
index = 0

host = input("Please enter the ip address: ")
username = input("Please enter the username: ")
password = getpass.getpass("Please enter the password: ")

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password)
stdin, stdout,stderr = client.exec_command("python3 pi_rotor_communicator.py", timeout=3600)

while stdout.readline() == "":
	continue

#listen to local port for rotctld commands
listen_ip = '127.0.0.1'  #listen on localhost
listen_port = 4533     #pass this from command line in future?
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind((listen_ip, listen_port))
client_socket.listen(1)

print ('Listening for rotor commands on', listen_ip, ':', listen_port)
conn, addr = client_socket.accept()
print ('Connection from ',addr)

while 1:
	data = conn.recv(100)  #get Gpredict's message
	if not data:
		continue

	decoded = data.decode("utf-8")
	#print(decoded)
	stdin.write(decoded)
	stdin.flush()

	cmd = decoded.strip().split(" ")   #grab the incoming command
	print("Received: ",cmd[0])    #debugging
	
	if cmd[0] == "p":   #Gpredict is requesting current position
		response = "{}\n{}\n".format(current_az, current_el)
		print(response)
		conn.send(response.encode('utf-8'))
		
	elif cmd[0] == "P":   #Gpredict is sending desired position
		current_az = float(cmd[1])
		current_el = float(cmd[2])

		test = stdout.readline()

		while test == "":
			print(test)
			test = stdout.readline()
			continue

		#Tell Gpredict things went correctly
		response="RPRT 0\n"  #Everything's under control, situation normal 
		conn.send(response.encode('utf-8'))
						
		#stdin.write(bytes(b'q\r')) #go back to Carryout's root menu
		
		
	elif cmd[0] == "S": #Gpredict says to stop
		print('Gpredict disconnected, exiting') 
		conn.close()
		client.close()
		exit()
	else:
		print('Exiting')
		conn.close()
		client.close()
		exit()



