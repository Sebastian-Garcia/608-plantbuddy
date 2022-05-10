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

                try:
                    with sqlite3.connect(plant_reading_db) as c:
                        c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, type text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
                        readings = c.execute('''SELECT * FROM plant_reading_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchall()
                        sunlight_reading = readings[0][0]
                        temp_reading = readings[0][1]
                        soil_reading = readings[0][1]
                except:
                    pass


                return htmlString.format(n=plantName, pt= plantType, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)
        except:
            return htmlString.format(n=plantName, pt= plantType, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)

        
    elif request['method'] =="POST":
        try:
            if 'form' in request.keys() and 'from' not in request["form"]:
                user = request['form']['user']
                plantName = request['form']['name']
                plantType = request['form']['type']
                sunlight = request['form']['light']
                temperature = request['form']['temp']
                moisture = request['form']['soil']
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
                sunlight_reading = float(info["sunlight"])
                temp_reading = float(info["temp"])
                soil_reading = float(info["moisture"])
                # with sqlite3.connect(plant_db) as c:
                #     # sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
                #     # moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
                #     # temperature = c.execute('''SELECT temperature FROM plant_data  WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
                #     #c.execute('''INSERT into plant_data VALUES (?,?,?,?);''',(plant,sunlight,temperature, moisture))
                #     things = c.execute('''SELECT * FROM plant_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
                #     c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (sunlight_reading real, temperature_reading real, moisture_reading real);""")
                with sqlite3.connect(plant_reading_db) as c:
                    c.execute('''INSERT into plant_reading_data VALUES (?,?,?);''',(sunlight_reading,temp_reading,soil_reading))
                    readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
                outs = {"plant": things[0][0], "sunlight": things[0][1], "temperature": things[0][2], "moisture": things[0][3]}
                plantName = outs['plant']
                sunlight = outs['sunlight']
                temperature = outs['temperature']
                moisture = outs['moisture']

                return

        
        
        
        except:
            return "invalid HTTP method for this url."


def do_plant_logic():
    pass