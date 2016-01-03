'''
Created on Dec 17, 2014

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

#cfsfd = ctypes.cdll.LoadLibrary('/home/sergio/iibm/sandbox/t.so')
#cfsfd.get_dc.restype = ctypes.c_float
#dc = cfsfd.get_dc("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54")
#print dc

def get_dc():
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    query = """SELECT spike.p1, spike.p2, spike.p3 from SPIKE 
                JOIN segment ON id_segment = segment.id 
                JOIN recordingchannel ON id_recordingchannel = recordingchannel.id  
                WHERE segment.id_block = 54 
                AND recordingchannel.index = 3"""
    
    cursor = dbconn.cursor()
    cursor.execute(query)
    
    results = cursor.fetchall()
    
    distances = []
    
    for i in range(len(results)):
        p1 = results[i]
        for j in range(len(results)):
            p2 = results[j]
            distances.append(((float(p1[0])-float(p2[0]))**2 + (float(p1[1])-float(p2[1]))**2 + (float(p1[2])-float(p2[2]))**2)**0.5)
    
    distances.sort()
    
    position = len(results)*2/100 -1;
    
    return distances[position];

def ajuste(n, coeficientes):
    vajuste = np.zeros(n)
    for j in range(n):
        vajuste[j] = np.polynomial.polynomial.polyval(j, coeficientes)
        
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
    
    libcd.get_clusters.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, array_1d_double, array_1d_double, array_1d_double, ctypes.c_int, ctypes.c_float]
    libcd.get_clusters.restype = ctypes.c_int
    
    libcd.get_n_dbspikes.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    libcd.get_n_dbspikes.restype = ctypes.c_int
    
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_block = "54"
    channel = "3"
    points = 3
    
#     t1 = time.time() 
    dc = libcd.get_dc(connect, id_block, channel, np.float(1.2), points)
#     t2 = time.time ()
#     print ((t2-t1)), dc
    #print dc
    #dc = 96.817154
    #dc = 90.160072
    #dc = 0.687492
    n = libcd.get_n_dbspikes(connect, id_block, channel)
    
    local_density = np.empty(n)
    distance_to_higher_density = np.empty(n)
    spikes_id = np.empty(n)
    clusters_index = np.empty(n)
    
    libcd.cluster_dp(connect, id_block, channel, local_density,
                     distance_to_higher_density, spikes_id, 
                     clusters_index, dc, points, "gaussian")
    
#     plt.plot(local_density, distance_to_higher_density, 'o')
#     plt.show()

    delta = distance_to_higher_density[local_density.argsort()]
    rho = local_density
    rho.sort()
    
    dp = np.empty(n)
    for i in range(len(rho)):
        dp[i] = delta[i]*rho[i]
    
    delta2 = np.copy(delta)
    delta2[:len(delta)*0.3] = 0
    
    coeficientes, stats= np.polynomial.polynomial.polyfit(range(n), dp, 1, full=True)
    dpajuste = ajuste(n, coeficientes)
    dpdesvio = (stats[0][0]/float(n))**0.5
    
    coeficientes, stats= np.polynomial.polynomial.polyfit(range(n), delta2, 1, full=True)
    deltaajuste = ajuste(n, coeficientes)
    deltadesvio = (stats[0][0]/float(n))**0.5
    
#     plt.subplot(2,1,1)
#     plt.plot(dp, 'bo')
#     plt.plot(dpajuste, 'g')
#     plt.plot(dpajuste + dpdesvio*1.5, 'r')
#     
#     plt.subplot(2,1,2)
    plt.plot(delta2, 'bo')
    plt.plot(deltaajuste, 'g')
    plt.plot(deltaajuste + deltadesvio*2.5, 'r')
    plt.show()
    centers = [0]
    j = 0
    for i in range(n):
        if (np.abs(delta2[i]-deltaajuste[i]))>2.5*deltadesvio:
            centers.append(i)
            j = j+1
    
    centers[0] = j
    
    centers = np.array(centers, np.float64)
    
    libcd.get_clusters(connect, id_block, channel, centers, spikes_id, clusters_index, 10, dc)
    
    
    for i in range(int(clusters_index.max())+1):
        plt.subplot(int(clusters_index.max())+1,1,i+1)
        for j in range(1026):
            if clusters_index[j] == i:
                spikes = neodb.core.spikedb.get_from_db(dbconn, id_block = 54, channel = 3, id = int(spikes_id[j]))
                signal = spikes[0].waveform
                plt.plot(signal)
    plt.show()
    print centers
   
#     gamma = distance_to_higher_density[local_density.argsort()]
#     local_density.sort()
#     
#     dp = np.empty(1026)
#     for i in range(len(gamma)):
#         dp[i] = gamma[i]*local_density[i]
# #     
# #     mean = dp.mean()
# #     
# #     a = np.empty(1026)
# #     a.fill(mean*2.3)
#     #plt.plot(dp, 'o')
#     #plt.plot(a, 'red')
#     #plt.show()
#     
#     gamma[:1026*0.3] = 0
#     coeficientes, stats= np.polynomial.polynomial.polyfit(range(1026), gamma, 1, full=True)
#     
#     ajuste = np.zeros(1026)
#     desvio = 0
#     for j in range(1026):
#         ajuste[j] = np.polynomial.polynomial.polyval(j, coeficientes)
#     
#     desvio = (stats[0][0]/1026.0)**0.5
#     
#     centers = []
#     for i in range(1026):
#            if gamma[i]>2*desvio:
#                centers.append(i)
#     
#     print centers
    
#     plt.subplot(3,1,1)
#     plt.plot(gamma, 'o')
#     plt.subplot(3,1,2)
#     plt.plot(local_density, gamma, 'o')
#     plt.subplot(3,1,3)
    
#     plt.plot(local_density, gamma, 'o')
#     plt.plot(local_density, dp, 'ro')
#     #plt.plot(ajuste, 'red')
#     plt.show()
    
    
#     centers = []
#     centers.append(0)
#     for i in range(int(len(dp)*0.25), len(dp)):
#         if dp[i]>2.5*mean:
#             centers.append(i)
#             centers[0] = centers[0] + 1
#     
#     centers = np.array(centers, dtype=np.float64)
    pass