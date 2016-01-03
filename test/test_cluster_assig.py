'''
Created on Mar 16, 2015

@author: sergio
'''
import numpy as np
import ctypes
import numpy.ctypeslib as npct
import matplotlib.pyplot as plt
import psycopg2
import time
import neurodb.neodb.core
from math import e, pow
from scipy.optimize import leastsq
from mpl_toolkits.mplot3d import Axes3D
from neurodb.cfsfdp import libcd

def get_points(id_block, channel):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    query = """SELECT spike.p1, spike.p2, spike.p3 from SPIKE 
                JOIN segment ON id_segment = segment.id 
                JOIN recordingchannel ON id_recordingchannel = recordingchannel.id  
                WHERE segment.id_block = %s 
                AND recordingchannel.index = %s"""%(id_block, channel)
    
    cursor = dbconn.cursor()
    cursor.execute(query)
    
    results = cursor.fetchall()
    
    points = []
    
    for i in range(len(results)):
        p1 = results[i][0]
        p2 = results[i][1]
        p3 = results[i][2]
        
        points.append([p1,p2,p3])
        
    return np.array(points)


def ajuste(local_density, coeficientes):
    vajuste = np.zeros(len(local_density))
    for j in range(len(local_density)):
        vajuste[j] = np.polynomial.polynomial.polyval(local_density[j], coeficientes)
        
    return vajuste




if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_block = "76"
    id_project = 19
    channel = "1"
    points = 3
    
    project = neurodb.project.get_from_db(id_project)
    session = project.get_session(int(id_block))
    channels = session.get_channels()
    
    for ch in channels:
        if ch['channel']==int(channel):
            rc = session.get_channel(ch['id'])
    
    spikes = rc.get_spikes()
    spikes_id = np.array(spikes, np.float64)
    
    dc = libcd.get_dc(connect, spikes_id, len(spikes), np.float(1.8), points)
    #dc = 0.221948802471
    #dc = 0.225272163749
    print dc
    
    n = len(spikes)
    
    local_density = np.empty(n)
    distance_to_higher_density = np.empty(n)
    #spikes_id = np.empty(n)
    cluster_index = np.empty(n)
    nneigh = np.empty(n)
    centers = np.empty(n)
    
    libcd.cluster_dp(connect, local_density, distance_to_higher_density,
                     spikes_id, cluster_index, nneigh, centers, dc, 
                     points, len(spikes), "gaussian")
    
    delta = np.copy(distance_to_higher_density)
    rho = np.copy(local_density)
    
    max = rho.max()
    max = int(max*0.06)
    print max
    for j in range(len(delta)):
        if (rho[j] < max):
            delta[j] = 0
    
#     plt.plot(local_density, distance_to_higher_density, 'bo')
#     plt.show()
    
    coeficientes1, stats1= np.polynomial.polynomial.polyfit(rho, delta, 1, full=True)
    
    ajuste1 = ajuste(rho, coeficientes1)
    desvio1 = (stats1[0][0]/float(n))**0.5
    
    plt.plot(rho, delta, 'bo')
    plt.plot(rho, ajuste1, 'r')
    plt.plot(rho, ajuste1 + 1.7*desvio1, 'g')
    plt.show()
    
    ordrho = local_density.argsort()[::-1]
    
    for i in range(n):
        if (cluster_index[ordrho[i]] == -1):
            cluster_index[ordrho[i]] = cluster_index[int(nneigh[ordrho[i]])];
        
#     for i in range(int(cluster_index.max())+1):
#         plt.subplot(int(cluster_index.max())+1,1,i+1)
#         k = 0
#         for j in range(n):
#             if cluster_index[j] == i:
#                 spikes = neurodb.neodb.core.spikedb.get_from_db(dbconn, id_block = id_block, channel = channel, id = int(spikes_id[j]))
#                 signal = spikes[0].waveform
#                 plt.plot(signal)
#                 k = 1 + k
#           
#         title = str(i) +": "+ str(k)
#         plt.title(title)
#     plt.show()
    
    for i in range(int(cluster_index.max())+1):
        for j in range(n):
            if cluster_index[j] == i:
                spikes = neurodb.neodb.core.spikedb.get_from_db(dbconn, id_block = id_block, channel = channel, id = int(spikes_id[j]))
                signal = spikes[0].waveform
                plt.plot(signal)
        #title = str(i)
        #plt.title(title)
        plt.show()
         
        
        
  #  plt.show()

    
    
    pass
