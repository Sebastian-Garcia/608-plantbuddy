from curses import echo
import requests
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import json



plant_db = '/var/jail/home/team58/plantbuddy/plants.db' 
plant_reading_db = '/var/jail/home/team58/plantbuddy/plants_reading.db' 
plant_sampling_db = '/var/jail/home/team58/plantbuddy/plants_sampling.db' 


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
            if len(request['values'].keys()) == 0 :
                with sqlite3.connect(plant_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, sunlight real, temperature real, moisture real );""")
                    things = c.execute('''SELECT * FROM plant_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
                with sqlite3.connect(plant_reading_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (sunlight_reading real, temperature_reading real, moisture_reading real);""")
                    readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
                outs = {"plant": things[0][0], "sunlight": things[0][1], "temperature": things[0][2], "moisture": things[0][3]}
                reading_outs = {"sunlight_reading": readings[0][0], "temperature_reading": readings[0][1], "moisture_reading": readings[0][2]}
                plant = outs['plant']
                sunlight = outs['sunlight']
                temperature = outs['temperature']
                moisture = outs['moisture']
                sunlight_reading = reading_outs['sunlight_reading']
                temp_reading = reading_outs['temperature_reading']
                soil_reading = reading_outs['moisture_reading']
                return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)
            plant = request["values"]["plant"]
            with sqlite3.connect(plant_db) as c:
                c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, sunlight real, temperature real, moisture real );""")
                things = c.execute('''SELECT * FROM plant_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
            with sqlite3.connect(plant_reading_db) as c:
                c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (sunlight_reading real, temperature_reading real, moisture_reading real);""")
                readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
            outs = {"plant": things[0][0], "sunlight": things[0][1], "temperature": things[0][2], "moisture": things[0][3]}
            reading_outs = {"sunlight_reading": readings[0][0], "temperature_reading": readings[0][1], "moisture_reading": readings[0][2]}
            plant = outs['plant']
            sunlight = outs['sunlight']
            temperature = outs['temperature']
            moisture = outs['moisture']
            sunlight_reading = reading_outs['sunlight_reading']
            temp_reading = reading_outs['temperature_reading']
            soil_reading = reading_outs['moisture_reading']
            return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)
        except:
            return "error or plant doesn't exist"
        
        

        # if "esp32" in request['values']:
        #     sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ?;''',(plant,)).fetchall()
        #     moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ?;''',(plant,)).fetchall()
        #     return (sunlight[0][0], moisture[0][0])
        
    elif request['method'] =="POST":
        # if 'form' in request.keys() and 'from' not in request["form"]:
        #     user = request['form']['owner']
        #     plant = request['form']['name']
        #     sunlight = request['form']['light']
        #     temperature = request['form']['temp']
        #     moisture = request['form']['soil']
        #     with sqlite3.connect(plant_db) as c:
        #         c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, sunlight real, temperature real, moisture real);""")
        #         c.execute('''INSERT into plant_data VALUES (?,?,?,?);''',(plant,sunlight,temperature, moisture))
        #     with sqlite3.connect(plant_reading_db) as c:
        #         readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
        #     reading_outs = {"sunlight_reading": readings[0][0], "temperature_reading": readings[0][1], "moisture_reading": readings[0][2]}
        #     sunlight_reading = reading_outs['sunlight_reading']
        #     temp_reading = reading_outs['temperature_reading']
        #     soil_reading = reading_outs['moisture_reading']
        #     return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading) 
        # elif 'form' in request.keys() and 'from' in request["form"] and 'arduino' == request["form"]['from']:
        #     info = request["form"]
        #     sunlight_reading = float(info["sunlight"])
        #     temp_reading = float(info["temp"])
        #     soil_reading = float(info["moisture"])
        #     with sqlite3.connect(plant_db) as c:
        #         # sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
        #         # moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
        #         # temperature = c.execute('''SELECT temperature FROM plant_data  WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
        #         #c.execute('''INSERT into plant_data VALUES (?,?,?,?);''',(plant,sunlight,temperature, moisture))
        #         things = c.execute('''SELECT * FROM plant_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
        #         c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (sunlight_reading real, temperature_reading real, moisture_reading real);""")
        #     with sqlite3.connect(plant_reading_db) as c:
        #         c.execute('''INSERT into plant_reading_data VALUES (?,?,?);''',(sunlight_reading,temp_reading,soil_reading))
        #         readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
        #     outs = {"plant": things[0][0], "sunlight": things[0][1], "temperature": things[0][2], "moisture": things[0][3]}
        #     plant = outs['plant']
        #     sunlight = outs['sunlight']
        #     temperature = outs['temperature']
        #     moisture = outs['moisture']

        #     return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)

        
        
        
        
    # else:
        return "invalid HTTP method for this url."