'''
Created on Jul 16, 2015

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
import multiprocessing as mp
from timeit import timeit
from time import time

# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL) 

def count_elapsed_time(f):
    """
    Decorator.
    Execute the function and calculate the elapsed time.
    Print the result to the standard output.
    """
    def wrapper():
        # Start counting.
        start_time = time()
        # Take the original function's return value.
        ret = f()
        # Calculate the elapsed time.
        elapsed_time = time() - start_time
        print("Elapsed time: %0.10f seconds." % elapsed_time)
        return ret
    
    return wrapper

def __select_nodes(id_project, id_session, channel, n_nodos):
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

def get_centers(connect, nodo, points, output):
    centersT = []
    
    spikes_id = np.array(nodo, np.float64)
    nspikes = len(spikes_id)
    
    local_density = np.empty(nspikes)
    distance_to_higher_density = np.empty(nspikes)
    cluster_index = np.empty(nspikes)
    nneigh = np.empty(nspikes)
    centers = np.empty(nspikes)
    
    dc = libcd.get_dc(connect, spikes_id, nspikes, np.float(1.8), points)
    libcd.cluster_dp(connect, local_density, distance_to_higher_density, spikes_id, 
                     cluster_index, nneigh, centers, dc, points, nspikes, "gaussian")
    
    #print "nodo procesado. ncenters:%s"%(int(centers[0]))
    
    ncenters = centers[0]
    
    for j in range(int(centers[0])):
        centersT.append([local_density[int(centers[j+1])], distance_to_higher_density[int(centers[j+1])]])
    
    output.put((centersT, ncenters, cluster_index))
    return (centersT, ncenters, cluster_index)

def get_centers_s(connect, nodo, points):
    centersT = []
    
    spikes_id = np.array(nodo, np.float64)
    nspikes = len(spikes_id)
    
    local_density = np.empty(nspikes)
    distance_to_higher_density = np.empty(nspikes)
    cluster_index = np.empty(nspikes)
    nneigh = np.empty(nspikes)
    centers = np.empty(nspikes)
    
    dc = libcd.get_dc(connect, spikes_id, nspikes, np.float(1.8), points)
    libcd.cluster_dp(connect, local_density, distance_to_higher_density, spikes_id, 
                     cluster_index, nneigh, centers, dc, points, nspikes, "gaussian")
    
    #print "nodo procesado. ncenters:%s"%(int(centers[0]))
    
    ncenters = centers[0]
    
    for j in range(int(centers[0])):
        centersT.append([local_density[int(centers[j+1])], distance_to_higher_density[int(centers[j+1])]])
    
    return (centersT, ncenters, cluster_index)

def paralelo():
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_project = 19
    id_session = "69"
    channel = "1"
    points = 6
    n_nodos = 25
    
    output = mp.Queue()
    processes = []
    
    nodos = __select_nodes(id_project, id_session, channel, n_nodos)
    
    for i in range(n_nodos):
        processes.append(mp.Process(target=get_centers, args=(connect, nodos[i], points, output)))
    
    for p in processes:
        p.start()
    
    for p in processes:
        p.join()
    
    results = [output.get() for p in processes]
    
    return results


def proc_multiproc():
    centers = []
    ncenters = 0
    results = paralelo()
    
    for res in results:
        if centers != []:
            centers = np.concatenate((centers, res[0]))
        else:
            centers = res[0]
        ncenters = res[1] + ncenters
             
    nclusters = np.ceil(ncenters/n_nodos)
    
    return centers, nclusters
    

def proc_serial():
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_project = 19
    id_session = "69"
    channel = "1"
    points = 6
    n_nodos = 25
    
    centers = []
    rho = np.array([], np.float64)
    delta = np.array([], np.float64)
    ncenters = 0
    
    nodos = __select_nodes(id_project, id_session, channel, n_nodos)
    
    for i in range(n_nodos):
        nodo = nodos[i]
        (c, nc, cl) = get_centers_s(connect, nodo, points)
        
        if centers != []:
            centers = np.concatenate((centers, c))
        else:
            centers = c
        ncenters = nc + ncenters
    
    nclusters = np.ceil(ncenters/n_nodos)
    
    return centers, nclusters

@count_elapsed_time
def test_serial():
    for i in range(20):
        proc_serial()
        
@count_elapsed_time
def test_multiproc():
    for i in range(20):
        proc_multiproc()

if __name__ == '__main__':    
    color = ['bo', 'ro', 'go', 'co', 'ko', 'mo', 'b^', 'r^', 'g^', 'c^', 'k^', 'm^']
    centers = []
    rho = np.array([], np.float64)
    delta = np.array([], np.float64)
    ncenters = 0
    n_nodos = 20
    
    ###### Procesamiento en paralelo
#     results = paralelo()
#     
#     for res in results:
#         if centers != []:
#             centers = np.concatenate((centers, res[0]))
#         else:
#             centers = res[0]
#         ncenters = res[1] + ncenters
#              
#     nclusters = np.ceil(ncenters/n_nodos)
    
    #### Fin de proc en paralelo
    
#     centers, nclusters = proc_multiproc()
#     
#     aw = AgglomerativeClustering(linkage='ward', n_clusters=int(nclusters))
#     aw.fit(centers)
#       
#     for i in range(len(centers)):
#         plt.plot(centers[i][0], centers[i][1], color[int(aw.labels_[i])])
#       
#     plt.show()
    
    
    ###### Procesamiento en Serie
    #centers, nclusters = proc_serial()
    
    print "Test paralelo"
    test_multiproc()
     
    print "Test serial"
    test_serial()
    
    pass