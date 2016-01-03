'''
Created on Mar 5, 2015

@author: sergio
'''

import numpy as np
import matplotlib.pyplot as plt
import psycopg2


def generar():
    mean = np.array([0,0])
    cov = np.array([[2,0],[0,2]])
    array1 = np.random.multivariate_normal(mean, cov, 500)
    
    mean = np.array([10,-10])
    cov = np.array([[2,0],[0,2]])
    array2 = np.random.multivariate_normal(mean, cov, 500)
    
    mean = np.array([0,-10])
    cov = np.array([[2,0],[0,2]])
    array3 = np.random.multivariate_normal(mean, cov, 500)
    
    plt.plot(array1[:,0], array1[:,1], 'o')
    plt.plot(array2[:,0], array2[:,1], 'ro')
    plt.plot(array3[:,0], array3[:,1], 'go')
    
    plt.show()
    
    
    
    
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname) 
     
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    cursor = dbconn.cursor()
    
    for i in range(500):
        query = "INSERT INTO spike (id_segment, id_recordingchannel,p1,p2) VALUES (%s,%s,%s,%s)"%(137, 82, float(array1[i,0]), float(array1[i,1]))
        cursor.execute(query)
    
    for i in range(500):
        query = "INSERT INTO spike (id_segment, id_recordingchannel,p1,p2) VALUES (%s,%s,%s,%s)"%(137, 82, float(array2[i,0]), float(array2[i,1]))
        cursor.execute(query)
    
    for i in range(500):
        query = "INSERT INTO spike (id_segment, id_recordingchannel,p1,p2) VALUES (%s,%s,%s,%s)"%(137, 82, float(array3[i,0]), float(array3[i,1]))
        cursor.execute(query)
    
    dbconn.commit()

def generararchivo():
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname) 
    
    dbconn = psycopg2.connect("dbname=demo host=172.16.162.128 user=postgres password=postgres")
    cursor = dbconn.cursor()
    
    query = """select p1, p2 from SPIKE 
           JOIN segment ON id_segment = segment.id 
           JOIN recordingchannel ON id_recordingchannel = recordingchannel.id 
           WHERE segment.id_block = 54
           AND recordingchannel.index = 5"""
           
    cursor.execute(query)
    
    results = cursor.fetchall()
    
    file = open("/home/sergio/iibm/data_figure_2/distancias2.txt", "w")
    for j in range(len(results)):
        for i in range(j+1,len(results)):
            p1 = results[j]
            p2 = results[i]
            dist = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(0.5)
            file.write("%s %s %s\n"%(j+1, i+1, dist))
    
    file.close()
if __name__ == '__main__':
    generararchivo()
    pass