'''
Created on Dec 22, 2013

@author: Sergio Hinojosa Rojas
'''
import ConfigParser  

# CFUNCTIONS_PATH = None
# REGISTERS_PATH = None
# TEMP_FOLDER = None
# PROJECT_PATH = None
# 
# # DB config
# DBHOSTNAME = None
# DBUSER = None
# DBPASSWORD = None
# DBNAME = None

# def loadConfig():
#     cfg = ConfigParser.ConfigParser()  
#     if not cfg.read(["~/.ndb.ini"]):  
#         print "No existe el archivo"
#     
#     global CFUNCTIONS_PATH
#     global REGISTERS_PATH
#     global TEMP_FOLDER
#     global PROJECT_PATH
#     
#     # DB config
#     global DBHOSTNAME
#     global DBUSER
#     global DBPASSWORD
#     global DBNAME
#     
#     DBHOSTNAME = cfg.get("database","hostname")
#     DBUSER = cfg.get("database","user")
#     DBPASSWORD = cfg.get("database","password")
#     DBNAME = cfg.get("database","dbname")

CFUNCTIONS_PATH = '/home/sergio/iibm/workspace2/NeuroDB/src/NeuroDB/cfunctions'
REGISTERS_PATH = '/home/sergio/iibm/workspace/NeuroDB/test/registers'
TEMP_FOLDER = '/tmp/neurodbtmp'
PROJECT_PATH = ''
 
# DB config
DBHOSTNAME = '172.16.162.128'
DBUSER = 'postgres'
DBPASSWORD = 'postgres'
DBNAME = 'demo'

