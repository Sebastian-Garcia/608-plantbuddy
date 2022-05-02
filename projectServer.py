#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 17:26:06 2022

@author: hermonkaysha
"""
import requests
import sqlite3
from bs4 import BeautifulSoup
#import pandas as pd


# names_list = []
# moisture_list = []
# shade_list = []
# for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
#     URL = "https://pfaf.org/user/DatabaseSearhResult.aspx?LatinName={web_letter}%".format(web_letter=letter)
#     page = requests.get(URL)

#     soup = BeautifulSoup(page.text, 'html.parser')
#     dfs = pd.read_html(page.text)
#     info = dfs[1]
#     names_list += info['Latin Name'][0:len(info['Latin Name'])-1].tolist()
#     moisture_list += info['Moisture'][0:len(info['Moisture'])-1].tolist()
#     shade_list += info['Shade'][0:len(info['Shade'])-1].tolist()




ht_db = '/var/jail/home/sebagarc/plants.db' 
#ht_db = 'plants.db' 


def request_handler(request):
    htmlString = """
    <!DOCTYPE html>
    <html>
    <body style="background-color:#a0d977;">

    <h2>Plant Entry Form</h2>

    <form action="projectServer.py" method="post">
    <label for="name">Plant name:</label><br>
    <input type="text" id="name" name="name"><br><br>
    <label for="owner">Owner:</label><br>
    <input type="text" id="owner" name="owner"><br><br>
    <label for="light">Hours of sunlight:</label><br>
    <input type="text" id="light" name="light"><br><br>
    <label for="temp">Temperature range:</label><br>
    <input type="text" id="temp" name="temp"><br><br>
    <input type="submit" value="Submit">
    </form> 

    <p>The "Submit" button will upload the data to the database.</p>
    <h2>--------------------------------------------------</h2>
    <h2>Other plant data, when created, will appear below.</h2>
    </body>
    </html>"""




    if request['method'] =="GET":
        try:
            if len(request['values'].keys()) == 0 :
                
                return htmlString
            if request['values']['database'] == "show":
                conn = sqlite3.connect(ht_db)
                c = conn.cursor()
                things = c.execute('''SELECT * FROM plant_data;''').fetchall()
                conn.commit()
                conn.close()
                return things
            plant = request["values"]["plant"]
            with sqlite3.connect(ht_db) as c:
                c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, sunlight real, moisture real);""")
                sunlight = c.execute('''SELECT sunlight FROM plant_data WHERE plant = ?;''',(plant,)).fetchall()
                moisture = c.execute('''SELECT moisture FROM plant_data  WHERE plant = ?;''',(plant,)).fetchall()
                
                return (sunlight[0][0], moisture[0][0])
        except:
            return "error or plant doesn't exist"
        
    elif request['method'] =="POST":
        plant = ""
        sunlight = ""
        moisture = ""
        if 'form' in request.keys():
            user = request['form']['owner']
            plant = request['form']['name']
            sunlight = request['form']['light']
            moisture = request['form']['temp']
        else: #This is for when we integrate the online web scraping data
            plant = request["values"]["plant"]
            found = False
            index = -1
            for name in names_list:
                if name == plant:
                    found = True
                index += 1
            if found:
                sunlight = shade_list[index]
                moisture = moisture_list[index]
            else:
                return "couldn't find plant in API"

        
        with sqlite3.connect(ht_db) as c:
             c.execute("""CREATE TABLE IF NOT EXISTS plant_data (plant text, sunlight real, moisture real);""")
             c.execute('''INSERT into plant_data VALUES (?,?,?);''',(plant,sunlight,moisture))
        return "Data POSTED successfully"
        
    else:
        return "invalid HTTP method for this url."
        
print(request_handler({"method": "GET","values":{"plant":"Alnus serrulata"}}))