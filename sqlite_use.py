#!/usr/bin/python3
import sqlite3
import os
import sys

def sql_help():
    print("<db> import it rather than use...")
    print("<db> put some useful things here")

def script_path():
    path = os.path.realpath(os.path.dirname(sys.argv[0]))
    os.chdir(path)  #it seems to be quite important
    return path

def clear_db(dbName="zperson_stuff.db"):
    #it will remove all data and create new db
    try:
        if os.path.exists(dbName):
            os.remove(dbName)       #physically remove db file
        db = sqlite3.connect(dbName)
        c = db.cursor()
        #for table in tables:
        #    print(table[0])
        #    c.execute('''DROP TABLE {}'''.format(table[0]))
        c.execute('CREATE TABLE IF NOT EXISTS {}(data TEXT, national TEXT, sex TEXT)'.format("names"))
        c.execute('CREATE TABLE IF NOT EXISTS {}(data TEXT, national TEXT)'.format("surnames"))
        tables = get_tables(dbName)
        print("<db> database tables: {}".format(tables))
        db.commit()
        c.close()
        db.close()
        print("<db> database file remove and created at new: {}".format(dbName))
        return True
    except:
        print("failed to remove db file: {}".format(dbName))
        return False
    
def get_tables(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    except sqlite3.DatabaseError as err:
        print("file is not a database...")
        return False
    tables = c.fetchall()
    return tables
    
def data_from_db(TABLE_NAME, toGet, getBy=[]):
    db = sqlite3.connect("zperson_stuff.db")
    c = db.cursor()
    if not getBy:
        data = c.execute('SELECT {0} FROM {1}'.format(toGet, TABLE_NAME))
    else:
        if TABLE_NAME == "names":
            #data = c.execute('SELECT {0} FROM {1} WHERE national={2} AND sex={3}'.format(toGet, TABLE_NAME, getBy[0], getBy[1]))
            data = c.execute('SELECT {0} FROM {1} WHERE national="{2}" AND sex="{3}"'.format(toGet, TABLE_NAME, getBy[0], getBy[1]))
        elif TABLE_NAME == "surnames":
            data = c.execute('SELECT {0} FROM {1} WHERE national="{2}"'.format(toGet, TABLE_NAME, getBy[0]))
    dataOut = [x[0] for x in data]
    db.commit()
    c.close()
    db.close()  
    return dataOut

def read_file(file_name, rmnl=False):
    '''read specified file and remove newlines depend on "rmnl" parameter'''
    path = os.path.realpath(os.path.dirname(sys.argv[0]))
    path = os.path.join(path, file_name)
    try:
        with open(path, "r") as file:
            if rmnl:
                fileContent = file.read().splitlines()
            else:
                fileContent = file.readlines()
    except:
        fileContent = []
    return fileContent    

def parse_config(config):
    '''parse config file, to get table name, and additional data'''
    config = [item.lower() for item in config]      #get it to the floor
    if config:
        table_name = config[0]
        if table_name == "names":
            if len(config) > 2:
                national = config[1]
                sex = config[2]
                if not sex in ("male", "female"):
                    print("<db> wrong sex: {} should be 'male' or 'female'".format(table_name))
                    return "", []
                additional = [national, sex]
            else:
                print("<db> no enough config args: {}".format(config))
                return "", []
        elif table_name == "surnames":
            if len(config) > 1:
                national = config[1]
                additional = [national]
            else:
                print("<db> no enough config args: {}".format(config))
                return "", []                
        else:
            print("<db> wrong table_name: {} should be 'names' or 'surnames'".format(table_name))
            return "", []
        
        return table_name, additional
    else:
        print("<db> no config to parse: {}".format(config))
        return "", []

def update_db(file, interactive=False):
    '''update database with specified file. Interactive mode is optional'''
    if not os.path.isfile(file):
        print("<db> you specified wrong file: {}".format(file))
        return False
    content = read_file(file, True)
    if not content:
        print("<db> wrong file specified, or empty one")
        return False
    else:
        config = content[0].split(",")
        data = content[1:]
    #replace rubbish:
    toReplace = [",", ".", "/"]
    for sign in toReplace:
        data = [item.replace(sign, " ") for item in data] 
    
    if interactive:
        #data = [item.replace("/", " ") for item in data]
        print("<db> data format in file:")
        if len(data) > 2:
            for x in range(3):
                print(data[x])
        for item in data:
            #to catch first non-blanc line
            columns = len(item.split())
            if columns:
                break                
        print("<db> columns number:", columns)
        columnNo = input("<db> choose column to update with: 0-{}\n".format(columns))
        if not str(columnNo) in [str(x) for x in range(columns)]:
            print("<db> wrong column specified")
            return False
        else:
            columnNo = int(columnNo)
        data = [item.split()[columnNo] for item in data if item]    #'if item' helps with empty lines
        print("<db> data to update:", data)
        if input("<db> do you want to update with? (y/n)\n").lower() in "y":
            pass
        else:
            return False
        
    db = sqlite3.connect("zperson_stuff.db") #if 1st time it creates new db
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {}(data TEXT, national TEXT, sex TEXT)'.format("names"))
    c.execute('CREATE TABLE IF NOT EXISTS {}(data TEXT, national TEXT)'.format("surnames"))
    
  
    table_name, additional = parse_config(config)
    #print("--< table_name: {}\n--< additional: {}".format(table_name, additional))
    if not table_name or not additional:
        print("<db> wrong config file")
        print("<db> write 1st line, and other data like in example below")
        print("\tnames,poland,male")
        print("\tZenon")
        print("\tLudwik")
        return False
    else:
        #remove whitespaces and join additional
        data = [tuple([item.strip()] + additional) for item in data if item]        
        print("<db> data to update:\n{}".format(data))       
    
    if table_name == "names":
        c.executemany('INSERT INTO %s VALUES (?,?,?)' % table_name, data)
    elif table_name == "surnames":
        c.executemany('INSERT INTO %s VALUES (?,?)' % table_name, data)
    else:
        return False
    
    db.commit()
    c.close()
    db.close()        
    return True
    
    
if __name__ == "__main__":
    #path = script_path()
    #clear_db()
    sql_help()
    
   
'''names & surnames:
https://en.wikipedia.org/wiki/Lists_of_most_common_surnames

https://en.wikipedia.org/wiki/List_of_most_common_surnames_in_Asia
https://en.wikipedia.org/wiki/List_of_most_common_surnames_in_Europe
https://en.wikipedia.org/wiki/List_of_most_common_surnames_in_North_America
https://en.wikipedia.org/wiki/List_of_most_common_surnames_in_Oceania
https://en.wikipedia.org/wiki/List_of_most_common_surnames_in_South_America

https://en.wikipedia.org/wiki/List_of_most_popular_given_names#Americas

'''