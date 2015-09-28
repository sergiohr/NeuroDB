import os
import config

pwd = os.getcwd()
os.sys.path.append(pwd)

import db

db.connect(user=config.DBUSER, password=config.DBPASSWORD, hostname=config.DBHOSTNAME, dbname=config.DBNAME)

import project
import individual
import features