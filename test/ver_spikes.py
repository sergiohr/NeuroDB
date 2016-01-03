'''
Created on May 12, 2015

@author: sergio
'''

import matplotlib.pyplot as plt
import neurodb.neodb.core
import psycopg2

if __name__ == '__main__':
    
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    project = 19
    id_block = "75"
    channel = "1"
    points = 6
    nnodos = 10
    
    id_spike = [154243, 155511]
    n = len(id_spike)
    for j in range(n):
        spikes = neurodb.neodb.core.spikedb.get_from_db(dbconn, id_block = id_block, channel = channel, id = int(id_spike[j]))
        signal = spikes[0].waveform
        plt.plot(signal)

    plt.show()   
    
    
    
    pass