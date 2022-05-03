import requests
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import json



#webscraper
# names_list = []
# moisture_list = []
# shade_list = []
# for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
#     URL = 'https://pfaf.org/user/DatabaseSearhResult.aspx?LatinName={web_letter}%'.format(web_letter=letter)
#     page = requests.get(URL)
#     print(page)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     dfs = pd.read_html(page.text)
#     info = dfs[1]
#     names_list += info['Latin Name'][0:len(info['Latin Name'])-1].tolist()
#     moisture_list += info['Moisture'][0:len(info['Moisture'])-1].tolist()
#     shade_list += info['Shade'][0:len(info['Shade'])-1].tolist()




plant_db = '/var/jail/home/team58/plantbuddy/plants.db' 
plant_reading_db = '/var/jail/home/team58/plantbuddy/plants_reading.db' 


def request_handler(request):
    htmlString = """
    <!DOCTYPE html>
    <html>
    <body style="background-color:#a0d977;">
    <h2>Plant Form</h2>
    <form action="server.py" method="post">
    <label for="name">Plant Name:</label><br>
    <input type="text" id="name" name="name"><br><br>
    <label for="owner">Owner:</label><br>
    <input type="text" id="owner" name="owner"><br><br>
    <label for="light">Hours of sunlight:</label><br>
    <input type="text" id="light" name="light"><br><br>
    <label for="temp">Temperature range:</label><br>
    <input type="text" id="temp" name="temp"><br><br>
    <label for="temp">Soil moisture:</label><br>
    <input type="text" id="soil" name="soil"><br><br>
    <input type="submit" value="Submit">
    </form> 
    <p>The "Submit" button will upload the data to the database.</p>
    <h2>--------------------------------------------------</h2>
    <h2>Plant Info</h2>
    <a>Plant name: {n}</a>
    <br>
    <a>Plant owner: {o}</a>
    <br>
    <a>Hours of sunlight needed: {s}</a>
    <br>
    <a>Temperature: {t}</a>
    <br>
    <a>Soil moisture: {m}</a>
    <h2>--------------------------------------------------</h2>
    <h2>Current Conditions</h2>
    <a>Hours of sunlight needed:{sr}</a>
    <br>
    <a>Temperature: {tr}</a>
    <br>
    <a>Soil moisture: {mr}</a>
    </body>
    </html>"""


    plant = 'no information yet'
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
            # if request['values']['database'] == "show":
            #     conn = sqlite3.connect(plant_db)
            #     c = conn.cursor()
            #     things = c.execute('''SELECT * FROM plant_data;''').fetchall()
            #     conn.commit()
            #     conn.close()
            #     return things
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
                # sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ?;''',(plant,)).fetchall()
                # moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ?;''',(plant,)).fetchall()
                # temperature = c.execute('''SELECT temperature FROM plant_data  WHERE plant = ?;''',(plant,)).fetchall()
            #return (outs['plant'], outs['sunlight'], outs['temperature'], outs['moisture'])
            return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)
        except:
            return "error or plant doesn't exist"
        
        

        # if "esp32" in request['values']:
        #     sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ?;''',(plant,)).fetchall()
        #     moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ?;''',(plant,)).fetchall()
        #     return (sunlight[0][0], moisture[0][0])
        
    elif request['method'] =="POST":
        if 'form' in request.keys() and 'from' not in request["form"]:
            user = request['form']['owner']
            plant = request['form']['name']
            sunlight = request['form']['light']
            temperature = request['form']['temp']
            moisture = request['form']['soil']
            with sqlite3.connect(plant_db) as c:
                c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, sunlight real, temperature real, moisture real);""")
                c.execute('''INSERT into plant_data VALUES (?,?,?,?);''',(plant,sunlight,temperature, moisture))
            with sqlite3.connect(plant_reading_db) as c:
                readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
            reading_outs = {"sunlight_reading": readings[0][0], "temperature_reading": readings[0][1], "moisture_reading": readings[0][2]}
            sunlight_reading = reading_outs['sunlight_reading']
            temp_reading = reading_outs['temperature_reading']
            soil_reading = reading_outs['moisture_reading']
            return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading) 
        elif 'form' in request.keys() and 'from' in request["form"] and 'arduino' == request["form"]['from']:
            info = request["form"]
            sunlight_reading = float(info["sunlight"])
            temp_reading = float(info["temp"])
            soil_reading = float(info["moisture"])
            with sqlite3.connect(plant_db) as c:
                # sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
                # moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
                # temperature = c.execute('''SELECT temperature FROM plant_data  WHERE plant = ? ORDER BY rowid DESC LIMIT 1;''',(plant,)).fetchall()
                #c.execute('''INSERT into plant_data VALUES (?,?,?,?);''',(plant,sunlight,temperature, moisture))
                things = c.execute('''SELECT * FROM plant_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
                c.execute("""CREATE TABLE IF NOT EXISTS plant_reading_data (sunlight_reading real, temperature_reading real, moisture_reading real);""")
            with sqlite3.connect(plant_reading_db) as c:
                c.execute('''INSERT into plant_reading_data VALUES (?,?,?);''',(sunlight_reading,temp_reading,soil_reading))
                readings = c.execute('''SELECT * FROM plant_reading_data ORDER BY rowid DESC LIMIT 1;''').fetchall()
            outs = {"plant": things[0][0], "sunlight": things[0][1], "temperature": things[0][2], "moisture": things[0][3]}
            # sr = float(info["sunlight"])
            # tr = float(info["temperature"])
            # mr = float(info["moisture"])
            plant = outs['plant']
            sunlight = outs['sunlight']
            temperature = outs['temperature']
            moisture = outs['moisture']
            
            # if sunlight_reading < float(sunlight) - 2:
            #     sunlight_reading = str(sunlight_reading) + ' TOO LITTLE SUNLIGHT!'
            # elif sunlight_reading > float(sunlight) + 2:
            #     sunlight_reading = str(sunlight_reading) + ' TOO MUCH SUNLIGHT!'
            # if temp_reading < float(temperature) - 10:
            #     temp_reading = str(temp_reading) + ' TOO COLD!'
            # elif temp_reading > float(temperature) + 10:
            #     sunlight_reading = str(temp_reading) + ' TOO HOT!'
            # if soil_reading < float(moisture) - 10:
            #     soil_reading = str(soil_reading) + ' TOO LITTLE WATER!'
            # elif soil_reading > float(moisture) + 10:
            #     soil_reading = str(soil_reading) + ' TOO MUCH WATER!'

            return htmlString.format(n=plant, o=user, s=sunlight, t=temperature, m=moisture, sr=sunlight_reading, tr=temp_reading,mr=soil_reading)
        
        # else: #This is for when we integrate the online web scraping data
        #     plant = request["values"]["plant"]
        #     found = False
        #     index = -1
        #     for name in names_list:
        #         if name == plant:
        #             found = True
        #         index += 1
        #     if found:
        #         sunlight = shade_list[index]
        #         moisture = moisture_list[index]
        #     else:
        #         return "couldn't find plant in API"

        
        
        
        
    else:
        return "invalid HTTP method for this url."