'''
Created on Feb 2, 2015

@author: sergio
'''

import psycopg2
import ConfigParser
import os

def get_config_folder():
    """Return path of de config.ini. If it does not exist, function create it in ~/.neodb"""
    base_path = os.path.expanduser('~')
    path = base_path + '/.neodb'
    if os.path.isdir(path) == False:
        os.mkdir(path)
    
    return path

def save_config(key, value):
    if key in ['host', 'user', 'password']:
        section = 'server'
    elif key in ['dbname', 'dbuser', 'dbpassword']:
        section = 'database'
    else:
        raise StandardError("Invalid key '%s'."%key)
    
    fichero = get_config_folder() + "/config.ini"
    parser = ConfigParser.SafeConfigParser()
    try:
        sf = open(fichero,"r+")
    except IOError:
        sf = open(fichero,"w")
        
        setsection = 'server'
        parser.add_section(setsection)
        parser.set(setsection, 'host', '')
        parser.set(setsection, 'user', '')
        parser.set(setsection, 'password', '')
        
        setsection = 'database'
        parser.add_section(setsection)
        parser.set(setsection, 'dbname', '')
        parser.set(setsection, 'dbuser', '')
        parser.set(setsection, 'dbpassword', '')
        
    parser.read(fichero)
    parser.set(section, key, value)
    
    parser.write(sf)
    sf.close()

def read_config(key):
    if key in ['host', 'user', 'password']:
        section = 'server'
    elif key in ['dbname', 'dbuser', 'dbpassword']:
        section = 'database'
    else:
        raise StandardError("Invalid key '%s'."%key)
    
    fichero = get_config_folder() + "/config.ini"
    parser = ConfigParser.SafeConfigParser()
    
    try:
        sf = open(fichero,"r+")
    except IOError:
        sf = open(fichero,"w")
        setsection = 'server'
        parser.add_section(setsection)
        setsection = 'database'
        parser.add_section(setsection)
        sf.close()
        
    parser.read(fichero)
    value = parser.get(section,key)
    
    if value == '':
        raise StandardError("Key '%s' is not configured."%key)
    
    return value
    
def config_server(host, username, password, dbname, dbuser, dbpassword):
    """Load config.ini with parameters of connection to db"""
    save_config('host', host)
    save_config('user', username)
    save_config('password', password)
    save_config('dbname', dbname)
    save_config('dbuser', dbuser)
    save_config('dbpassword', dbpassword)

def dbconnect(dbname = None, username = None, password = None, host = None):
    if not dbname:
        dbname = read_config('dbname')
    if not username:
        username = read_config('dbuser')
    if not password:
        password = read_config('dbpassword')
    if not host:
        host = read_config('host')
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    return dbconn

if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    config_server(host, username, password, dbname, username, password)
    pass