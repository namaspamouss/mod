#!/usr/bin/python3.4

import sqlite3
import time
import urllib.request
import json
import datetime
import os
import RPi.GPIO as GPIO
import my_logger as log


#####################################
#                                   #
#  MM     MM    OOOOO    DDDDDD     #
#  MMM   MMM   OO   OO   DDD  DDD   #
#  MMMM MMMM  OO     OO  DD    DDD  #
#  MM MMM MM  OO     OO  DD     DD  #
#  MM  M  MM  OO     OO  DD     DD  #
#  MM     MM  OO     OO  DD    DDD  #
#  MM     MM   OO   OO   DDD  DDD   #
#  MM     MM    OOOOO    DDDDDD     #
#                                   #
# -------- My Own Domoticz -------- #
#####################################


class Probe():
    def __init__(self, name, IDX, constructor_id, temp = 20.0):
        self.name = name
        self.IDX = IDX
        self.constructor_id = constructor_id
        self.temp = temp

probes = [
    Probe("salon", 79, "28-80000026b0d0"),
    Probe("chambre1", 80, "28-80000026c0ee"),
    Probe("chambre2", 81, "28-80000026a7a5")
]
"""
probes = [
	Probe("cuisine", 75, "28-8000000859cf"),
	Probe("cellier", 76, "28-80000026a7d4"),
	Probe("couloir", 77, "28-80000026c380"),
	Probe("salle de bain", 78, "28-8000000859bd")
]
"""

# obviously this part is about your Domoticz server, not the server where this progam is running
domoticz_server_address = "192.168.1.20"
domoticz_server_port = "8080"

security_temp = 33.3

def emergency_w1_restart():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)
    time.sleep(30)
    GPIO.output(17, GPIO.HIGH)
    time.sleep(60)


def check_db_exist():
    try:
        with sqlite3.connect('mydb.db') as conn:
            cursor = conn.cursor()
            try:
            	# is a sqlite database already set ?
                cursor.execute("SELECT probe, value, time, server_response FROM temp_value ORDER BY time DESC LIMIT 1")
                return "database ready"
            except Exception as e:
            	# if not, just create it !
                cursor.execute("CREATE TABLE temp_value(ID INTEGER PRIMARY KEY AUTOINCREMENT, probe TEXT NOT NULL, value REAL NOT NULL, time REAL NOT NULL, server_response TEXT);")
                conn.commit()
                return "database created"
    except Exception as e:
        log.log_file("Error","oups! error in check_if_db_file_exist -> {}".format(e))


def get_data_from_ds18b20(probe) :
    try:
        with open("/sys/bus/w1/devices/"+probe.constructor_id+"/w1_slave") as fichTemp:
            data = fichTemp.read()
        first_line = data.split("\n")[0]
        probe_state = first_line.split(" ")[11]
        
        secondeLigne = data.split("\n")[1]
        temperatureData = secondeLigne.split(" ")[9]
        temperature = float(temperatureData[2:])
        # Suppressing the "t="
        temperature = temperature / 1000
        temperature = "{0:0.1f}".format(temperature)
        # adding one digit after the point
        temperature = float(temperature)
        probe.temp = temperature
        #log.log_file("DEBUG", "probe_state of {} is {} and temp is {}".format(probe.name, probe_state, probe.temp))
        time.sleep(5)
        return temperature
    except FileNotFoundError as e:
    	# if the file is not found, the main possible cause could be an overloaded probe
        log.log_file("Warning","probe:{} not found but retrying later....".format(probe.name))
        time.sleep(60)
    except Exception as e:
        log.log_file("Error", "oups! error in get_data_from_ds18b20 -> {}".format(e))


def send_to_domoticz(probe):
    try:
        cmd = "http://"+domoticz_server_address+":"+domoticz_server_port+"/json.htm?type=command&param=udevice&idx="+str(probe.IDX)+"&nvalue=0&svalue="+str(probe.temp)
        with urllib.request.urlopen(cmd) as response:
            r = str(response.read(), 'utf8')
            r = json.loads(r)
            return r['status']
    except Exception as e:
        log.log_file("Error", "oups! error in send_to_domoticz -> {}".format(e))


def set_temp_value():
    try:
        with sqlite3.connect('mydb.db') as conn:
            for probe in probes:
                temp = get_data_from_ds18b20(probe)
                now = time.time()
                cursor = conn.cursor()
                server_response = send_to_domoticz(probe)
                cursor.execute("INSERT INTO temp_value (probe, value, time, server_response) VALUES ('{}','{}','{}','{}')".format(probe.name, probe.temp, now, server_response))
                #print(datetime.datetime.now(), ", probe: ",probe, " temp: ", temp, ", server_response: ", server_response)
        #print("\n")
    except Exception as e:
        conn.rollback()
        log.log_file("Error", "oups! error in set_temp_value -> {}".format(e))


# main code 
# i prefer to desactivate and reactivate the probes just in
# case they were overloaded in a previous run
if __name__ == "__main__":
    print(check_db_exist())
    log.log_file("Info","mod chambre started ...")
    while True:
        set_temp_value()
        time.sleep(60)



# everything written down here may be used in future
# be aware that nothing here uses my_logger
"""
def get_temp_value():
    try:
        with sqlite3.connect('mydb.db') as conn:
            print("opened database successfully")
            cursor = conn.cursor()
            cursor.execute("SELECT time, value FROM temp_value")
            data_set = cursor.fetchall()
            return data_set
    except Exception as e:
        conn.rollback()
        print("oups! error in get_temp_value -> {}".format(e))

# probe is in text like: "salon"
def get_last_temp_value(probe):
    try:
        with sqlite3.connect('mydb.db') as conn:
            print("opened database successfully")
            cursor = conn.cursor()
            cursor.execute("SELECT time, value FROM temp_value WHERE probe = '{}' ORDER BY time DESC LIMIT 1 ".format(probe))
            data_set = cursor.fetchall()
            return data_set
    except Exception as e:
        conn.rollback()
        print("oups! error in get_last_temp_value -> {}".format(e))
"""
