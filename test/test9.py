'''
Created on Feb 25, 2015

@author: sergio
'''


import numpy as np
import ctypes
import numpy.ctypeslib as npct
import matplotlib.pyplot as plt
import psycopg2
import time

from math import e, pow
from scipy.optimize import leastsq

if __name__ == '__main__':
#     username = 'postgres'
#     password = 'postgres'
#     host = '192.168.2.2'
#     dbname = 'demo'
#     url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname) 
#     
#     dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
#     cursor = dbconn.cursor()
    
    fi = open("/home/sergio/Downloads/fig2_panelB.dat", "r")
    fo = open("/home/sergio/iibm/cluster_dp/examples.dat", "w")
    
    a = fi.readline()
    
    p = []
    while(a != ""):
        b= a.split(' ')
#         query = "INSERT INTO spike (id_segment, id_recordingchannel,p1,p2) VALUES (%s,%s,%s,%s)"%(136, 81, float(b[0]), float(b[1]))
#         cursor.execute(query)
        
        p.append([float(b[0]),float(b[1])])
        a = fi.readline()
    
#     dbconn.commit()
    
    for i in range(len(p)):
        for j in range(i+1, len(p)):
            d = ((p[i][0]-p[j][0])**2 + (p[i][1]-p[j][1])**2)**0.5
            fo.write("%s %s %s\n"%(i+1, j+1, d))
    
    fo.close()
    fi.close()
    
    pass