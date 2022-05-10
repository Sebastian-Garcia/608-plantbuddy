import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sqlite3

plant_web_db = '/Users/timmydang/downloads/6.08/608-plantbuddy/plant_web.db' 


names_list = []
moisture_list = []
shade_list = []
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    URL = 'https://pfaf.org/user/DatabaseSearhResult.aspx?LatinName={web_letter}%'.format(web_letter=letter)
    #URL = 'https://pfaf.org/user/DatabaseSearhResult.aspx?LatinName=A%'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    dfs = pd.read_html(page.text)
    info_setup = dfs[1]
    info = info_setup[['Common Name', 'Moisture', 'Shade']].dropna()
    names_list += info['Common Name'][0:len(info['Common Name'])].tolist()
    moisture_list += info['Moisture'][0:len(info['Moisture'])].tolist()
    shade_list += info['Shade'][0:len(info['Shade'])].tolist()

# d = {'Name': names_list, 'Moisture': moisture_list, 'Shade': shade_list}
# df = pd.DataFrame(data=d)
# df.to_csv('plant_data.csv')


with sqlite3.connect(plant_web_db) as c:
    for i in range(len(names_list)):
        plant = names_list[i]
        sunlight = shade_list[i]
        moisture = moisture_list[i]
        c.execute("""CREATE TABLE IF NOT EXISTS plant_web (plant text, moisture real, sunlight real);""")
        #c.execute('''INSERT into plant_web VALUES (?,?,?);''',(plant,sunlight, moisture))
    things = c.execute('''SELECT DISTINCT plant FROM plant_web ORDER BY plant ASC;''').fetchall()

# print(names_list)
# print(moisture_list)
# print(shade_list)
# for i in range(len(results)-1):
#     if i <= 1:
#         continue
#     names = str(results[i].find("a"))
#     #name = re.search(r'>*+<', names)
#     start_name = names.find(">") + len(">")
#     end_name = names.find("</a>")
#     name = names[start_name:end_name]
#     names_list.append(name)

    # soils = str(results[i])[255:].split('<td>')[3]
    # end_soil = soils.find("<")
    # soil = soils[0:end_soil]
    # soils_list.append(soil)

#print(results[5])  
    
