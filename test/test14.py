'''
Created on Mar 12, 2015

@author: sergio
'''

import numpy as np
import ctypes
import numpy.ctypeslib as npct
import matplotlib.pyplot as plt
import psycopg2
import time
import neodb.core
from math import e, pow
from scipy.optimize import leastsq


def get_points(id_block, channel):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    query = """SELECT spike.p1, spike.p2 from SPIKE 
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
        
        points.append([p1,p2])
        
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
    
    array_1d_double = npct.ndpointer(dtype=np.double, ndim=1, flags='CONTIGUOUS')
    array_1d_int = npct.ndpointer(dtype=np.int64, ndim=1, flags='CONTIGUOUS')
    array_2d_double = npct.ndpointer(dtype=np.double, ndim=2, flags='CONTIGUOUS')
    
    libcd = npct.load_library("cfsfdp", "/home/sergio/Proyectos/NeuroDB/NeuroDB/NeuroDB/cfunctions/cfsfdp")
    
    libcd.get_dc.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_float, ctypes.c_int]
    libcd.get_dc.restype = ctypes.c_float
    
    libcd.cluster_dp.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, array_1d_double, array_1d_double, array_1d_double, array_1d_double, ctypes.c_float, ctypes.c_int, ctypes.c_char_p]
    libcd.cluster_dp.restype = ctypes.c_int
    
    libcd.get_n_dbspikes.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    libcd.get_n_dbspikes.restype = ctypes.c_int
    
    libcd.get_clusters.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, array_1d_double, array_1d_double, array_1d_double, ctypes.c_int, ctypes.c_float]
    libcd.get_clusters.restype = ctypes.c_int
    
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_block = "54"
    channel = "3"
    points = 5
    
    #dc = libcd.get_dc(connect, id_block, channel, np.float(1.2), points)
    #dc = 91.58
    #dc = 39.23
    dc = 60.12
    
    n = libcd.get_n_dbspikes(connect, id_block, channel)
    
    local_density = np.empty(n)
    distance_to_higher_density = np.empty(n)
    spikes_id = np.empty(n)
    cluster_index = np.empty(n)
    centers = []
    
    libcd.cluster_dp(connect, id_block, channel, local_density,
                     distance_to_higher_density, spikes_id, 
                     cluster_index, dc, points, "gaussian")
     
#     plt.plot(local_density, distance_to_higher_density, 'bo')
#     plt.show()
            
    gamma = []
    for i in range(len(local_density)):
         gamma.append(local_density[i]*distance_to_higher_density[i])
    
    coeficientes1, stats1= np.polynomial.polynomial.polyfit(local_density, gamma, 1, full=True)
    
    ajuste1 = ajuste(local_density, coeficientes1)
    desvio1 = (stats1[0][0]/float(n))**0.5
    
    plt.plot(local_density, gamma, 'bo')
    plt.plot(local_density, ajuste1, 'r')
    plt.plot(local_density, ajuste1 + 2*desvio1, 'g')
#     
    plt.show()
    
    centers.append(0);
    for i in range(len(gamma)):
        if (gamma[i] > ajuste1[i] + 2*desvio1):
            centers.append(i)
            centers[0] = centers[0] + 1
    
    print centers
    
    centers = np.array(centers, np.float64)
    
    libcd.get_clusters(connect, id_block, channel, centers, spikes_id, cluster_index, points, dc)
    
    for i in range(int(cluster_index.max())+1):
        plt.subplot(int(cluster_index.max())+1,1,i+1)
        k = 0
        for j in range(1026):
            if cluster_index[j] == i:
                spikes = neodb.core.spikedb.get_from_db(dbconn, id_block = 54, channel = 3, id = int(spikes_id[j]))
                signal = spikes[0].waveform
                plt.plot(signal)
                k = 1 + k
        
        title = str(i) +": "+ str(k)
        plt.title(title)
    plt.show()

    
    
    pass
