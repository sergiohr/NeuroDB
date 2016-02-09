'''
Created on Jun 27, 2015

@author: sergio
'''

from neurodb.cfsfdp import libcd
import numpy as np
import neurodb
import random
import matplotlib.pyplot as plt
import pickle
from sklearn.cluster import KMeans, AgglomerativeClustering, MiniBatchKMeans, Birch, SpectralClustering

def ajuste(n, coeficientes):
    vajuste = np.zeros(n)
    for j in range(n):
        vajuste[j] = np.polynomial.polynomial.polyval(j, coeficientes)
        
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


def cluster(local_density, distance_to_higher_density):
    n = len(local_density)
    local_density2 = np.empty(n)
    distance_to_higher_density2 = np.empty(n)
    
    distances = np.empty(n*n)
    
    for i in range(n):
        for j in range(n):
            x1=local_density[i]
            x2=local_density[j]
            y1=distance_to_higher_density[i]
            y2=distance_to_higher_density[j]
            distances[int(i*n+j)] = np.power(np.power(x1-x2,2)+np.power(y1-y2,2),0.5)
    
    dc = np.sort(distances)[int(n*0.2+n)]
    
    print "#############"
    print dc
    
#     libcd.get_distance_to_higher_density()
#     libcd.get_local_density()
    


if __name__ == '__main__':
    
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_project = 19
    id_session = "98"
    channel = "1"
    points = 6
    n_nodos = 1
    
    color = ['bo', 'ro', 'go', 'co', 'ko', 'mo', 'b^', 'r^', 'g^', 'c^', 'k^', 'm^']
    
    nodos = select_nodes(id_project, id_session, channel, n_nodos)
    n = len(nodos[0])
    
    local_density = np.empty(n)
    distance_to_higher_density = np.empty(n)
    cluster_index = np.empty(n)
    nneigh = np.empty(n)
    centers = np.empty(n)
    
    nodo = np.array(nodos[0], np.float64)
    dc = libcd.get_dc(connect, nodo, n, np.float(2), points)
    libcd.getDC(connect, features, spikes_id, nspikes, np.float(1.8), points)
    #dc = 5.83778190613
    #dc = 4.82201528549
    print dc
    
    f = open('distance_to_higher_density.p','rb')
    distance_to_higher_density = np.load(f)
    f.close()
       
    f = open('local_density.p','rb')
    local_density = np.load(f)
    f.close()
    
    rho = local_density
    delta = distance_to_higher_density
    
    delta = distance_to_higher_density[local_density.argsort()]
    rho = local_density
    rho.sort()
    
    coeficientes, stats= np.polynomial.polynomial.polyfit(range(n), delta, 1, full=True)
    ajuste = ajuste(n, coeficientes)
    
    delta[0:int(n*0.25)] = 0
    desvio = (stats[0][0]/float(n))**0.5
    
    plt.plot(rho,ajuste+(desvio*1.4))
    plt.plot(rho, delta, 'o')
    plt.show()
    
    
    
#     libcd.cluster_dp(connect, local_density, distance_to_higher_density, nodo, 
#          cluster_index, nneigh, centers, dc, points, n, "gaussian")
    
#     delta = distance_to_higher_density[local_density.argsort()]
#     rho = local_density
#     rho.sort()
    
    
    
#     km = KMeans(n_clusters = int(2))
#     aw = AgglomerativeClustering(linkage='complete', n_clusters=6)
#     spectral = SpectralClustering(n_clusters=3, eigen_solver='amg',
#                                   affinity="nearest_neighbors",
#                                   assign_labels='discretize',
#                                   n_neighbors=8,
#                                   degree=4)
# #     km.fit(np.array([rho, delta]).transpose())
#     aw.fit(np.array([rho, delta]).transpose())
#     #spectral.fit(np.array([rho, delta]).transpose())
#     
#     #cluster(local_density, distance_to_higher_density)
#     
#     for i in range(n):
#         plt.plot(rho[i], delta[i], color[int(aw.labels_[i])])

#     plt.plot(rho, delta, 'bo')
#     plt.plot(rho, ajuste, 'ro')
#     plt.show()
