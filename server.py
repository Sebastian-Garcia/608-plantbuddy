from curses import echo
import requests
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import json
import smtplib


plant_db = '/var/jail/home/team58/plantbuddy/plant.db' 
plant_reading_db = '/var/jail/home/team58/plantbuddy/plant_reading.db' 
plant_sampling_db = '/var/jail/home/team58/plantbuddy/plant_sampling.db' 

def send_notification(message, recipient="sebastianag2002@gmail.com"):

    message = "plant moisture levels are low, water in a few days"
    sender = "sebastiandeveloperemail@gmail.com"
    password = "Pikachu44!"

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, password)
    server.sendmail(sender, recipient, message)
    server.quit()

def request_handler(request):
    with open("/var/jail/home/team58/plantbuddy/plantPage.html", "r", encoding='utf-8') as f:
        htmlString= f.read()


    plantName = 'no information yet'
    plantType = 'no information yet'
    user = 'no information yet'
    sunlight = 'no information yet'
    temperature = 'no information yet'
    moisture = 'no information yet'
    sunlight_reading = 'no readings yet'
    temp_reading = 'no readings yet'
    soil_reading = 'no readings yet'

    if request['method'] =="GET":
        try:
                plantName = request["values"]["name"]
                user = request["values"]["user"]
                with sqlite3.connect(plant_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, type text, user text, sunlight real, temperature real, moisture real);""")
                    things = c.execute('''SELECT * FROM plant_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchall()
                    plantType = things[0][1]
                    sunlight = things[0][3]
                    temperature = things[0][4]
                    moisture = things[0][5]

                    moisture_percent = moisture/4096
                    if moisture_percent < .25:
                        moisture = "Very Low Watering Required"
                    elif moisture_percent < .50:
                        moisture = "Low Watering Required"
                    elif moisture_percent <.75:
                        moisture = "Medium Amount of Water Required"
                    else:
                        moisture = "High Amount of Water Required"

                try:
                    with sqlite3.connect(plant_reading_db) as c:
                        c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
                        readings = c.execute('''SELECT * FROM plant_reading_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchall()
                        sunlight_reading = readings[0][0]
                        temp_reading = readings[0][1]
                        soil_reading = readings[0][1]

                        soil_reading_percent = soil_reading/4096

                        if soil_reading_percent < .25:
                            soil_reading = "Very Low Water Level"
                        elif soil_reading_percent < .50:
                            soil_reading = "Low Water Level"
                        elif soil_reading_percent <.75:
                            soil_reading = "Medium Amount of Water"
                        else:
                            soil_reading = "High Amount of Water"
                except:
                    pass

                
                return htmlString.format(n=plantName, pt= plantType, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)
        except:
            return htmlString.format(n=plantName, pt= plantType, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)

        
    elif request['method'] =="POST":
        # return request
        try:
            if 'form' in request.keys() and 'submit' in request["form"]:
                user = request['form']['user']
                plantName = request['form']['name']
                plantType = request['form']['type']
                sunlight = request['form']['light']
                temperature = request['form']['temp']
                moisture = request['form']['soil']
                with sqlite3.connect(plant_sampling_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_sampling_data (plant text, user text, counter int);""")
                    sampling = c.execute('''SELECT * FROM plant_sampling_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchone()
                    c.execute('''INSERT into plant_sampling_data VALUES (?,?,?);''',(plantName,user,sampling[2]+1))
                with sqlite3.connect(plant_reading_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
                    c.execute('''INSERT into plant_reading_data VALUES (?,?,?,?,?);''',(plantName,user,0,0,0))
                return htmlString.format(n=plantName, pt=plantType, o=user, s=sunlight, t=temperature, m=moisture, sr="Pending", tr="Pending",mr="Pending")

            if 'form' in request.keys() and 'from' not in request["form"]:
                user = request['form']['user']
                plantName = request['form']['name']
                plantType = request['form']['type']

                if plantType == 'Snake Plant':
                    sunlight = 10
                    temperature = 10
                    moisture = 10
                elif plantType == 'Peace Lily':
                    sunlight = 20
                    temperature = 20
                    moisture = 20
                elif plantType == 'Fiddle Leaf Fig':
                    sunlight = 30
                    temperature = 30
                    moisture = 30
                elif plantType == 'Philodendron':
                    sunlight = 40
                    temperature = 40
                    moisture = 40
                elif plantType == 'ZZ Plant':
                    sunlight = 50
                    temperature = 50
                    moisture = 50
                elif plantType == 'Pothos':
                    sunlight = 60
                    temperature = 60
                    moisture = 60
                elif plantType == 'Majesty Palm':
                    sunlight = 70
                    temperature = 70
                    moisture = 70
                elif plantType == 'Aloe':
                    sunlight = 80
                    temperature = 80
                    moisture = 80
                else:
                    moisture = request['form']['soil']
                    sunlight = request['form']['light']
                    temperature = request['form']['temp']
                # add new plant to database
                with sqlite3.connect(plant_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, type text, user text, sunlight real, temperature real, moisture real);""")
                    c.execute('''INSERT into plant_data VALUES (?,?,?,?,?,?);''',(plantName,plantType,user,sunlight,temperature,moisture))
                # start a GET counter for new sampling device
                with sqlite3.connect(plant_sampling_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_sampling_data (plant text, user text, counter int);""")
                    c.execute('''INSERT into plant_sampling_data VALUES (?,?,?);''',(plantName,user,0))

                return htmlString.format(n=plantName, pt=plantType, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading) 

            # handle arduino post request
            elif 'form' in request.keys() and 'from' in request["form"] and 'arduino' == request["form"]['from']:
                info = request["form"]
                plantName = info["name"]
                user = info["user"]
                sunlight_reading = float(info["sunlight"])
                temp_reading = float(info["temperature"])
                soil_reading = float(info["moisture"])
                with sqlite3.connect(plant_reading_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
                    c.execute('''INSERT into plant_reading_data VALUES (?,?,?,?,?);''',(plantName,user,sunlight_reading,temp_reading,soil_reading))
                return

        
        
        
        except:
            return "invalid HTTP method for this url."


def do_plant_logic():
    pass