import sqlite3
import json

temp_db = '/var/jail/home/timmyd/milestone_1/temp_table.db'

def request_handler(request):

    conn = sqlite3.connect(temp_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    outs = ""
    c.execute('''CREATE TABLE IF NOT EXISTS temp_table (temp_num int);''') # run a CREATE TABLE command
    

    if request["method"] == "GET":
        things = c.execute('''SELECT * FROM temp_table ORDER BY rowid DESC LIMIT 1;''').fetchall()
        outs = {"temp_num": things[0][0]}
        return json.dumps(outs)
    elif request["method"] == "POST":
        temp_num = float(request['values']['temp_num'])
        c.execute('''INSERT into temp_table VALUES (?);''', (temp_num,))
        conn.commit()
        conn.close() 
        return temp_num