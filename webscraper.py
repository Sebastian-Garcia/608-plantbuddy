import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


names_list = []
moisture_list = []
shade_list = []
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    URL = "https://pfaf.org/user/DatabaseSearhResult.aspx?LatinName={web_letter}%".format(web_letter=letter)
    page = requests.get(URL)

    soup = BeautifulSoup(page.text, 'html.parser')
    dfs = pd.read_html(page.text)
    info = dfs[1]
    names_list += info['Latin Name'][0:len(info['Latin Name'])-1].tolist()
    moisture_list += info['Moisture'][0:len(info['Moisture'])-1].tolist()
    shade_list += info['Shade'][0:len(info['Shade'])-1].tolist()

#print(names_list)
#print(moisture_list)
print(shade_list)
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
    
