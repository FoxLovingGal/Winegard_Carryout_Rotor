import serial
import regex as re
import sys
import pandas as pd
from datetime import datetime, timedelta, timezone


try:

        #initialize some variables
        log = open("moveLog.txt", "a")
        current_az = 0.00
        current_el = 0.00
        failed_writes = 0
        failed_writes_row = 0
        total = 0


        #define "carryout" as the serial port device to interface with note we're def gonna need to change the port for>
        carryout = serial.Serial(
                port="/dev/ttyUSB0",
                baudrate = 115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1)



        carryout.write(bytes(b"q\r")) #go back to root menu in case firmware was left in a submenu
        carryout.write(bytes(b"\r")) #clear firmware prompt to avoid unknown command errors

        #opens up motor menu and homes the motors, this way we will not have to manually open it up every time we want >
        carryout.write(bytes(b"mot\r"))
        carryout.write(bytes(b"h *\r"))
        finished = ""
        reading = ""
        #keeps code in this while loop until the home command is done,
        while not finished:
                reading = carryout.read_all()
                try:
                        reading = reading.decode().strip()
                        finished = re.search(r"MOT>$", reading)
                except UnicodeDecodeError:
                        if b"MOT>$" in reading:
                                finished = "true"


        carryout.write(bytes(b"q\r"))
        
        
        pass_list = pd.read_csv("csv_files/target_list.csv")
        time_stamp = datetime.now()
        log.write("start of log " + str(time_stamp) + "\n")
        



        for index, row in pass_list.iterrows():
                #checks how far behind it is
                if  pd.to_datetime(pass_list.iloc[index]["Timestamp (UTC)"]).tz_localize("UTC") + timedelta(seconds=0.5) < datetime.now(timezone.utc):
                                continue

                #checks to see if we've hit a threshold of failed writes
                if failed_writes_row > 5:
                        print("more than five failed writes in a row ending program")
                        log.write("Total failed writes: " + str(failed_writes) + "\n")
                        log.write("End time stamp " + str(datetime.now()) + "\n")
                        log.write("failed writes rate: " + str(failed_writes/total) + "\n")
                        try:
                                carryout.close()
                        except NameError:
                                pass
                        sys.exit()

                target_az = row["Azimuth (deg)"]
                target_el = row["Elevation (deg)"]

                
                #cleaning out the buffer of the carryout
                while carryout.in_waiting != 0:
                        carryout.read_all()
                
                



                #tell Carryout to move to target position
                carryout.write(bytes(b"mot\r"))
                az_command = ("a 0 " + str(target_az) + "\r").encode("ascii")
                carryout.write(az_command)
                       
                reply = carryout.read_until(b"MOT>")
                reply = carryout.read_until(b"MOT>")
                        
                if not reply:
                    log.write("An error in writing/reading has occured")
                    failed_writes += 1
                    failed_writes_row += 1
                    total += 1
                else:
                     #print(reply)
                     try:
                            reply = reply.decode().strip()
                            match = re.search("= (\\d+\\.\\d+)", reply)
                            current_az = match.group(1).strip()
                            failed_writes_row = 0
                            total += 1
                     except UnicodeDecodeError:
                            log.write("An error in writing/reading has occured")
                            failed_writes += 1
                            failed_writes_row += 1
                            total += 1
                
                

                while carryout.in_waiting != 0:
                        carryout.read_all()

                time_stamp = datetime.now()
                log.write(row["Satellite"] + " first movement " + str(time_stamp) +"\n")

                el_command = ("a 1 " + str(target_el) + "\r").encode("ascii")
                #print("Command sent: " + el_command.decode())
                carryout.write(el_command)


                reply = carryout.read_until(b">")
                #print(reply)
                        
                if not reply:
                    log.write("An error in writing/reading has occured")
                    failed_writes += 1
                    failed_writes_row += 1
                    total += 1
                else:
                    try:
                        reply = reply.decode().strip()
                        match = re.search("= (\\d+\\.\\d+)", reply)
                        current_el = match.group(1).strip()
                        current_el = target_el
                        failed_writes_row = 0
                        total += 1
                    except UnicodeDecodeError:
                            log.write("An error in writing/reading has occured")
                            failed_writes += 1
                            failed_writes_row += 1
                            total += 1


                

                time_stamp = datetime.now()
                log.write(row["Satellite"] + " second movement " + str(time_stamp) +"\n")

                #print(match)
                carryout.write(bytes(b"q\r")) #go back to Carryout's root menu

                time_stamp = datetime.now()
                log.write(row["Satellite"] + " " + str(time_stamp) + ": " + str(current_az) + ", " + str(current_el) + "\n")    


                if(row["Satellite"] == pass_list.iloc[index + 1]["Satellite"]):
                        while pd.to_datetime(pass_list.iloc[index + 1]["Timestamp (UTC)"]).tz_localize("UTC") > datetime.now(timezone.utc):
                                pass
                else:
                        continue

except KeyboardInterrupt:
        print("\nending program")
        log.write("run was ended by user \n")
        log.write("Total failed writes: " + str(failed_writes) + "\n")
        log.write("failed writes rate: " + str(failed_writes/total) + "\n")
        log.write("End time stamp " + str(datetime.now()) + "\n")
        try:
                carryout.close()
        except NameError:
                pass
        sys.exit()