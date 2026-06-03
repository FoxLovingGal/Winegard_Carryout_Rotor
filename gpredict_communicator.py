#Python program to control Winegard Carryout as an AZ/EL Rotor from Gpredict
#This version created by Addison Wolf
#Credit to Gabe Emerson / Saveitforparts 2024, Email: gabe@saveitforparts.com for creating much of the base

import zmq
import sys
import socket 


try:

	#initialize some variables
	current_az = 0.00  
	current_el = 0.00
	index = 0

	ip = input("Please input IP of the Raspberry PI: ")

	#Connecting to the Raspberry Pi
	context = zmq.Context()
	print("Connecting to Raspberry Pi")
	pisocket = context.socket(zmq.REQ)
	pisocket.connect ("tcp://" + ip + ":5556")
	pisocket.RCVTIMEO = 240000 

	pisocket.send(b"Start up")
	reply = pisocket.recv().decode("utf-8")

	if(reply != "ready"):
		print("an error has occured, reply is: ", reply)
		pisocket.close()
		context.term()
		sys.exit()

	#listen to local port for rotctld commands
	listen_ip = '127.0.0.1'  #listen on localhost
	listen_port = 4533     
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


		cmd = decoded.strip().split(" ")   #grab the incoming command
		print("Received: ",cmd[0])    #debugging
		
		if cmd[0] == "p":   #Gpredict is requesting current position
			response = "{}\n{}\n".format(current_az, current_el)
			#print(response)
			conn.send(response.encode('utf-8'))
			
		elif cmd[0] == "P":   #Gpredict is sending desired position
			pisocket.send(decoded.encode('utf-8'))
			response = pisocket.recv().decode("utf-8")

			if(response != "clear"):
				print("server replied with unexpected value")
				context.term()
				conn.close()
				sys.exit()

			current_az = float(cmd[1])
			current_el = float(cmd[2])


			#Tell Gpredict things went correctly
			response="RPRT 0\n"  #Everything's under control, situation normal 
			conn.send(response.encode('utf-8'))
							
			
			
		elif cmd[0] == "S": #Gpredict says to stop
			pisocket.send(decoded.encode('utf-8'))
			print('Gpredict disconnected, exiting') 
			conn.close()
			pisocket.close()
			context.term()
			sys.exit()
		else:
			print('Exiting')
			conn.close()
			pisocket.close()
			context.term()
			sys.exit()

except KeyboardInterrupt:
	print("ending program")
	try:
		try:
			pisocket.close()
		except NameError:
			pass
		context.term()
	except NameError:
		pass
	try:
		conn.close()
	except NameError:
		pass
	sys.exit()

