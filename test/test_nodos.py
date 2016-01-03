'''
Created on Apr 5, 2015

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
import neurodb
import random
from sklearn.cluster import KMeans, AgglomerativeClustering, MiniBatchKMeans
from neurodb.cfsfdp import libcd

array_1d_double = npct.ndpointer(dtype=np.double, ndim=1, flags='CONTIGUOUS')
array_1d_int = npct.ndpointer(dtype=np.int64, ndim=1, flags='CONTIGUOUS')
array_2d_double = npct.ndpointer(dtype=np.double, ndim=2, flags='CONTIGUOUS')

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


def select_nodes(id_project, id_session, channel, n_nodos):
    project = neurodb.project.get_from_db(id_project)
    session = project.get_session(int(id_session))
    channels = session.get_channels()
    
    for ch in channels:
        if ch['channel']==int(channel):
            rc = session.get_channel(ch['id'])
    
    spikes = rc.get_spikes()
    
    random.shuffle(spikes)
    
    len_spikes = len(spikes)
    len_nodo = np.ceil(float(len_spikes)/float(n_nodos))
    
    nodos = []
    
    for i in range(n_nodos):
        nodo = []
        j = 0
        while(spikes != [] and j<len_nodo):
            nodo.append(spikes.pop())
            j = j + 1
            
        nodos.append(nodo)
    
    return nodos


def select_nodes_r(id_project, id_session, channel, n_nodos):
    project = neurodb.project.get_from_db(id_project)
    session = project.get_session(int(id_session))
    channels = session.get_channels()
    
    for ch in channels:
        if ch['channel']==int(channel):
            rc = session.get_channel(ch['id'])
    
    spikes = rc.get_spikes()
    
    len_spikes = len(spikes)
    len_nodo = np.ceil(float(len_spikes)/float(n_nodos))
    
    nodos = []
    
    for i in range(n_nodos):
        nodo = random.sample(spikes,int(len_nodo))            
        nodos.append(nodo)
    
    return nodos


def get_centers(nodos, nnodos, points):
    centersT = []
    rho = np.array([], np.float64)
    delta = np.array([], np.float64)
    ncenters = 0
    
    spikes = np.array([], np.float64)
    cl = np.array([], np.float64)
    
    for i in range(nnodos):
        spikes_id = nodos[i]
        spikes_id = np.array(spikes_id, np.float64)
        nspikes = len(spikes_id)
        
        local_density = np.empty(nspikes)
        distance_to_higher_density = np.empty(nspikes)
        cluster_index = np.empty(nspikes)
        nneigh = np.empty(nspikes)
        centers = np.empty(nspikes)
        
        dc = libcd.get_dc(connect, spikes_id, nspikes, np.float(1.8), points)
        libcd.cluster_dp(connect, local_density, distance_to_higher_density, spikes_id, 
                         cluster_index, nneigh, centers, dc, points, nspikes, "gaussian")
        
        print "nodo %s procesado. ncenters:%s"%(i,int(centers[0]))
        ncenters = centers[0] + ncenters
        
        for j in range(int(centers[0])):
            centersT.append([local_density[int(centers[j+1])], distance_to_higher_density[int(centers[j+1])]])
        
        rho = np.concatenate((rho,local_density))
        delta = np.concatenate((delta, distance_to_higher_density))
        
        spikes = np.concatenate((spikes, spikes_id))
        cl = np.concatenate((cl, cluster_index))
        
#         plt.plot(local_density, distance_to_higher_density, 'o')
#         plt.show()
    
    ncenters = np.ceil(ncenters/nnodos)
    plt.plot(rho, delta, 'ro')
    plt.show()
    
    centersT = np.array(centersT)
    
    return centersT, ncenters, spikes, cl



if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
        
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    project = 19
    id_block = "76"
    #id_block = "76"
    channel = "1"
    points = 3
    nnodos = 50
    
    nodos = select_nodes_r(project, id_block, channel, nnodos)
    
    color = ['bo', 'ro', 'go', 'co', 'ko', 'mo', 'b^', 'r^', 'g^', 'c^', 'k^', 'm^', 'bx', 'rx', 'gx', 'cx', 'kx', 'mx']
    
    centers, nclusters, spikes, cl= get_centers(nodos, nnodos, points)
    print "clusters: %s"%nclusters
    
    km = KMeans(n_clusters = int(nclusters))
    #km = MiniBatchKMeans(n_clusters = int(ncenters))
    aw = AgglomerativeClustering(linkage='ward', n_clusters=int(nclusters))
    
    km.fit(centers) 
    aw.fit(centers)
    
#     plt.plot(km.cluster_centers_[0][0], km.cluster_centers_[0][1], 'kx')
#     plt.plot(km.cluster_centers_[1][0], km.cluster_centers_[1][1], 'kx')
#     plt.plot(km.cluster_centers_[2][0], km.cluster_centers_[2][1], 'kx')
#     c = np.array(centers, np.float64)
#     
#     centersC = np.empty(len(c[:,1]))
#     labels = np.empty(len(c[:,1]))
#     x = np.array(c[:,0], np.float64)
#     y = np.array(c[:,1], np.float64)
#     libcd.dp(x, y, len(c[:,1]), labels, centersC, "gaussian")
    
    for i in range(len(centers)):
        plt.plot(centers[i][0], centers[i][1], color[int(aw.labels_[i])])
    
    plt.show()
    pass
    #
    
    
#     local_density = np.empty(nspikes)
#     distance_to_higher_density = np.empty(nspikes)
#     cluster_index = np.empty(nspikes)
#     nneigh = np.empty(nspikes)
#     centers = np.empty(nspikes)
#     
#     dc = libcd.get_dc(connect, spikes_id, nspikes, np.float(1.8), points)
#     libcd.cluster_dp(connect, local_density, distance_to_higher_density, spikes_id, 
#                      cluster_index, nneigh, centers, dc, points, nspikes, "gaussian")
#     
#     plt.plot(local_density, distance_to_higher_density, 'bo')
#     plt.show()
#     
#     for i in range(int(cluster_index.max())+1):
#         plt.subplot(int(cluster_index.max())+1,1,i+1)
#         k = 0
#         for j in range(nspikes):
#             if cluster_index[j] == i:
#                 spikes = neurodb.neodb.core.spikedb.get_from_db(dbconn, id_block = id_block, channel = channel, id = int(spikes_id[j]))
#                 signal = spikes[0].waveform
#                 plt.plot(signal)
#                 k = 1 + k
#           
#         title = str(i) +": "+ str(k)
#         plt.title(title)
#     plt.show()     
#     
#     pass
