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
    sunlight_intensity = 'no information yet'
    sunlight_hours = 'no information yet'
    temperature = 'no information yet'
    moisture = 'no information yet'
    sunlight_reading = 'no readings yet'
    temp_reading = 'no readings yet'
    soil_reading = 'no readings yet'

    if request['method'] =="GET":
            if "from" in request["values"].keys() and request["values"]["from"] == "arduino":
                plantName = request["values"]["name"]
                user = request["values"]["user"]
                with sqlite3.connect(plant_sampling_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_sampling_data (plant text, user text, counter int);""")
                    sampling = c.execute('''SELECT * FROM plant_sampling_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchone()
                    return sampling[2]
            else:
                try:
                    plantName = request["values"]["name"]
                    user = request["values"]["user"]
                    with sqlite3.connect(plant_db) as c:
                        c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, type text, user text, sunlight_intensity text, sunlight_hours real, temperature real, moisture real);""")
                        things = c.execute('''SELECT * FROM plant_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchall()
                        plantType = things[0][1]
                        sunlight_intensity = things[0][3]
                        sunlight_hours = things[0][4]
                        temperature = things[0][5]
                        moisture = things[0][6]

                        # moisture_percent = moisture/4096
                        # if moisture_percent < .25:
                        #     moisture = "Very Low Watering Required"
                        # elif moisture_percent < .50:
                        #     moisture = "Low Watering Required"
                        # elif moisture_percent <.75:
                        #     moisture = "Medium Amount of Water Required"
                        # else:
                        #     moisture = "High Amount of Water Required"
                        output_message = "Your Plant Buddy is currently gathering data!<br>Please wait it to finish :)<br> "

                    try:
                        with sqlite3.connect(plant_reading_db) as c:
                            c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
                            readings = c.execute('''SELECT * FROM plant_reading_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchall()
                            sunlight_reading = readings[0][2]
                            temp_reading = readings[0][3]
                            soil_reading = readings[0][4]

                            # soil_reading_percent = soil_reading/4096

                            # if soil_reading_percent < .25:
                            #     soil_reading = "Very Low Water Level"
                            # elif soil_reading_percent < .50:
                            #     soil_reading = "Low Water Level"
                            # elif soil_reading_percent <.75:
                            #     soil_reading = "Medium Amount of Water"
                            # else:
                            #     soil_reading = "High Amount of Water"
                            output_message = do_plant_logic(plantName, user)
                    except:
                        pass

                    return htmlString.format(n=plantName, pt= plantType, o=user, i=sunlight_intensity, s=sunlight_hours, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading,output=output_message)
                except:
                    return htmlString.format(n=plantName, pt= plantType, o=user, i=sunlight_intensity, s=sunlight_hours, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading,output="Find your plant!<br> ")

        
    elif request['method'] =="POST":
        # return request
        # try:
            # start new sampling POST request 
            if 'form' in request.keys() and 'submit' in request["form"]:
                user = request['form']['user']
                plantName = request['form']['name']
                plantType = request['form']['type']
                temperature = request['form']['temp']
                moisture = request['form']['soil']
                with sqlite3.connect(plant_sampling_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_sampling_data (plant text, user text, counter int);""")
                    sampling = c.execute('''SELECT * FROM plant_sampling_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plantName, user)).fetchone()
                    c.execute('''INSERT into plant_sampling_data VALUES (?,?,?);''',(plantName,user,sampling[2]+1))
                with sqlite3.connect(plant_reading_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
                    c.execute('''INSERT into plant_reading_data VALUES (?,?,?,?,?);''',(plantName,user,0,0,0))
                return htmlString.format(n=plantName, pt=plantType, o=user, i=sunlight_intensity, s=sunlight_hours, t=temperature, m=moisture, sr="Pending", tr="Pending",mr="Pending", output="Your Plant Buddy is currently gathering data!<br>Please wait it to finish :)<br> ")

            # add new plant POST request
            if 'form' in request.keys() and 'from' not in request["form"]:
                user = request['form']['user']
                plantName = request['form']['name']
                plantType = request['form']['type']

                if plantType == 'Snake Plant':
                    sunlight_intensity = 1393
                    sunlight_hours = 9
                    temperature = 21
                    moisture = 20
                elif plantType == 'Peace Lily':
                    sunlight_intensity = 300
                    sunlight_hours = 17
                    temperature = 22
                    moisture = 60
                elif plantType == 'Fiddle Leaf Fig':
                    sunlight_intensity = 500
                    sunlight_hours = 7
                    temperature = 21
                    moisture = 30
                elif plantType == 'Philodendron':
                    sunlight_intensity = 400
                    sunlight_hours = 7
                    temperature = 27
                    moisture = 60
                elif plantType == 'ZZ Plant':
                    sunlight_intensity = 100
                    sunlight_hours = 12
                    temperature = 20
                    moisture = 20
                elif plantType == 'Pothos':
                    sunlight_intensity = 300
                    sunlight_hours = 12
                    temperature = 60
                    moisture = 40
                elif plantType == 'Majesty Palm':
                    sunlight_intensity = 750
                    sunlight_hours = 7
                    temperature = 21
                    moisture = 60
                elif plantType == 'Aloe':
                    sunlight_intensity = 150
                    sunlight_hours = 7
                    temperature = 20
                    moisture = 20
                else:
                    moisture = request['form']['soil']
                    sunlight_intensity = request['form']['lightType']
                    sunlight_hours = request['form']['lightTime']
                    temperature = request['form']['temp']

                # add new plant to database
                with sqlite3.connect(plant_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, type text, user text, sunlight_intensity text, sunlight_hours real, temperature real, moisture real);""")
                    c.execute('''INSERT into plant_data VALUES (?,?,?,?,?,?,?);''',(plantName,plantType,user,sunlight_intensity,sunlight_hours,temperature,moisture))
                # start a GET counter for new sampling device
                with sqlite3.connect(plant_sampling_db) as c:
                    c.execute("""CREATE TABLE IF NOT EXISTS plant_sampling_data (plant text, user text, counter int);""")
                    c.execute('''INSERT into plant_sampling_data VALUES (?,?,?);''',(plantName,user,0))

                return htmlString.format(n=plantName, pt=plantType, o=user, i=sunlight_intensity, s=sunlight_hours, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading,output=do_plant_logic(plantName, user)) 

            # handle arduino POST request
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

        
        
        
        # except:
        #     return "invalid HTTP method for this url."


def do_plant_logic(plant, user):
    sunlight_reading = 0
    temp_reading = 0
    soil_reading = 0

    with sqlite3.connect(plant_db) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, type text, user text, sunlight_intensity text, sunlight_hours real, temperature real, moisture real);""")
        things = c.execute('''SELECT * FROM plant_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plant, user)).fetchone()
        ideal_sunlight_intensity = things[3]
        ideal_sunlight_hours = things[4]
        ideal_temp = things[5]
        ideal_moisture = things[6]
    
    try:
        with sqlite3.connect(plant_reading_db) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (plant text, user text, sunlight_reading real, temperature_reading real, moisture_reading real);""")
            readings = c.execute('''SELECT * FROM plant_reading_data WHERE plant = ? AND user = ? ORDER BY rowid DESC LIMIT 1;''', (plant, user)).fetchall()
            sunlight_reading = readings[0][2]
            temp_reading = readings[0][3]
            soil_reading = readings[0][4]
        
    except:
        pass

    if sunlight_reading == 0 and temp_reading == 0 and soil_reading == 0:
        return "Your Plant Buddy is currently gathering data!<br>Please wait it to finish :)<br> "
    
    output_message = ""

    if ideal_temp - temp_reading > 5:
        output_message += "Your plant is too hot! :(<br>"
    elif temp_reading - ideal_temp > 5:
        output_message += "Your plant is too cold! :(<br>"
    else:
        output_message += "Your plant is just the right temperature :)<br>"

    if ideal_sunlight_intensity == "Low":
        ideal_sunlight = 50 * ideal_sunlight_hours
    elif ideal_sunlight_intensity == "Medium":
        ideal_sunlight = 300 * ideal_sunlight_hours
    else:
        ideal_sunlight = 750 * ideal_sunlight_hours
    
    if (ideal_sunlight - sunlight_reading > 500):
        output_message += "Your plant needs more sunlight! :(<br>"
    elif (sunlight_reading - ideal_sunlight > 500):
        output_message += "Your plant needs less sunlight! :(<br>"
    else:
        output_message += "Your plant is getting enough sunlight :)<br>"

    if (ideal_moisture - soil_reading > 10):
        output_message += "Water your plant! :(<br> "
    elif (soil_reading - ideal_moisture > 10):
        output_message += "Your plant is overwatered! :(<br> "
    else:
        output_message += "Your plant is getting enough water :)<br> "
    
    return output_message