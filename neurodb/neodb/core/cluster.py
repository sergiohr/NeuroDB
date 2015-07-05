'''
Created on Jan 31, 2015

@author: sergio
'''

import psycopg2
import os

def save(connection, id_block, channel, clusters):
    cursor = connection.cursor()
    
    query = """DELETE 
               FROM cluster
               USING recordingchannel 
               WHERE id_recordingchannel = recordingchannel.id
               AND recordingchannel.id_block = %s 
               AND recordingchannel.index = %s """%(id_block, channel)
                     
    cursor.execute(query)
    connection.commit()
    
    query = """SELECT id
               FROM recordingchannel
               WHERE id_block = %s and 
                     recordingchannel.index = %s """%(id_block, channel)    
    cursor.execute(query)
    results = cursor.fetchall()
    
    id_recordingchannel = results[0][0]
    
    query = """INSERT INTO cluster (id_spike, id_recordingchannel, index) 
                   VALUES (%s, %s, %s)"""
                   
    ncluster = len(clusters)
    
    for i in range(ncluster):
        for id_spike in clusters[i]:
            cursor.execute(query,[id_spike, id_recordingchannel, i])
    
    connection.commit()

if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    save(dbconn, '54', '3',[])