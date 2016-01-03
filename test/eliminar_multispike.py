'''
Created on Jul 9, 2015

@author: sergio
'''

import numpy as np
import neurodb
import neurodb.neodb.core
import psycopg2
import matplotlib.pyplot as plt
import scipy


if __name__ == '__main__':
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_project = 19
    id_session = "76"
    channel = "1"
    points = 6
    n_nodos = 1
    sr = 32258
    
    dbconn = psycopg2.connect(connect)
    cursor = dbconn.cursor()
    
    project = neurodb.project.get_from_db(id_project)
    session = project.get_session(int(id_session))
    channels = session.get_channels()
    
    for ch in channels:
        if ch['channel']==int(channel):
            rc = session.get_channel(ch['id'])
    
    spikes = rc.get_spikes()
    
    for id in range(len(spikes)):
        spikedb = neurodb.neodb.core.spikedb.get_from_db(dbconn, id_session, channel, id=spikes[id])[0]
        ids = []
        spike = np.copy(spikedb.waveform)
        p_spike = np.copy(spike)
        n_spike = np.copy(spike)
        
        pnspk = 0
        nnspk = 0
        std = 1.1*np.std(spike)
        ones = np.ones(len(spike))
        
#         plt.plot(spike)
#         plt.plot(ones*std, 'r')
#         plt.plot(ones*(-std), 'r')
#         plt.show()
        
        for i in range(len(spike)):
        
            if spike[i] < std:
                p_spike[i] = 0
            
            if spike[i] > -std:
                n_spike[i] = 0
            else:
                n_spike[i] = -n_spike[i]
        
        pgr = np.gradient(p_spike)
        ngr = np.gradient(n_spike)
        
        for i in range(len(spike)-1):
            if pgr[i]>=0 and pgr[i+1] < 0 :
                pnspk = pnspk + 1
        
        for i in range(len(spike)-1):
            if ngr[i]>=0 and ngr[i+1] < 0 :
                nnspk = nnspk + 1
                
        if nnspk>=2 or pnspk>=2:
#             ids.append(id)
#             plt.plot(spike)
#             plt.show()
            spikedb.remove()
        
        
    #plt.show()
    pass
    
#     cursor.execute
#     
#     cursor.execute(query)
#     results = cursor.fetchall()
    
    pass