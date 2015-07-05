'''
Created on Apr 5, 2015

@author: sergio
'''


import psycopg2
import config
import neodb
import argparse

NDB = None

def connect(user=None, password=None, hostname=None, dbname=None):
    """connect_db(user=config.DBUSER, password=config.DBPASSWORD, hostname=config.DBHOSTNAME, dbname=config.DBNAME)
       
       Create connection NDB that establishes a real DBAPI connection to the database.
       Neurodb uses a database schema create by NeoDB
       
       Return
       Function returns object SQLAlchemy Connection
       """
    global NDB
    try:
        NDB = neodb.config.dbconnect(dbname, user, password, hostname)
    except argparse.ArgumentError:
        pass
    
    return NDB


if __name__ == '__main__':
    pass