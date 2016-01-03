'''
Created on Jul 31, 2015

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
from sklearn.decomposition import PCA
import neurodb.features

def get_features(spikes):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    p = ""
    for i in spikes:
        p = p + " id_spike=%s or"%(i)
    p = p[:len(p)-3]
    
    query = "SELECT id from FEATURES WHERE" + p
    
    cursor = dbconn.cursor()
    cursor.execute(query)
    
    results = cursor.fetchall()
    results = [x[0] for x in results]
        
    return np.array(results, np.float64)


def clustering(nodo, points, output):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    spikes_id = np.array(nodo, np.float64)
    #spikes_id1= np.copy(spikes_id)
    
    nspikes = len(nodo)
    
    rho = np.empty(nspikes)
    delta = np.empty(nspikes)
    nneigh = np.empty(nspikes)
    centers = np.empty(nspikes)
    
    cluster_index = np.empty(nspikes)
    features = get_features(nodo)
    
    #dc = libcd.get_dc(connect, spikes_id, nspikes, np.float(1.8), points)
    dc = libcd.getDC(connect, features, spikes_id, nspikes, np.float(1.8), points)
    
    #libcd.cluster_dp(connect, rho, delta, spikes_id, 
    #                     cluster_index1, nneigh, centers, dc, points, nspikes, "gaussian")
    libcd.dpClustering(features, nspikes, dc, points, "gaussian", spikes_id, cluster_index, rho, delta)
    
    templates = []
    spikes = []
    gspikes = []
    
    for i in range(1, int(cluster_index.max())+1):
        template = np.zeros(64, np.float64)
        k = 0
        for j in range(nspikes):
            if cluster_index[j] == i:
                spike = neurodb.neodb.core.spikedb.get_from_db(dbconn, 
                            id_block = id_block, channel = channel, id = int(spikes_id[j]))
                signal = spike[0].waveform
                template = template + signal
                gspikes.append(nodo[j])
                k = k + 1
        template = template/k
        templates.append(template)
        spikes.append(gspikes)
    
    output.put((templates, spikes))
    
    pass

def ajuste(local_density, coeficientes):
    vajuste = np.zeros(len(local_density))
    for j in range(len(local_density)):
        vajuste[j] = np.polynomial.polynomial.polyval(local_density[j], coeficientes)
        
    return vajuste

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

def insertFeaturesTemplate(templates, spike_ids):
    pca = PCA(n_components=10)
    transf = pca.fit_transform(templates)
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    #spike_ids = np.float16(spike_ids)
    
    cursor = dbconn.cursor()
    ids = []
    
    i = 0
    for x in transf:
        query = """INSERT INTO FEATURES (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, extra)
                      VALUES (%s, %s,%s, %s,%s, 
                              %s,%s, %s,%s, %s, %s) RETURNING id"""
        cursor.execute(query, [x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], 
                               x[8], x[9], psycopg2.Binary(np.float32(spike_ids[i]))])
        id_of_new_row = cursor.fetchone()[0]
        ids.append(id_of_new_row)
        i = i+1
    dbconn.commit()
    
    return ids


def getSpikeCluster(features_ids):
    
    
    
    pass


def serial(dbconn, nodos, output):
    for nodo in nodos:
        a = clustering(nodo, 3, output)
        
        result = output.get()
        for i in result[0]:
            plt.plot(i)
        plt.show()

if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    
    color = ['bo', 'ro', 'go', 'co', 'ko', 'mo', 'b^', 'r^', 'g^', 'c^', 'k^', 'm^']
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    centers = []
    rho = np.array([], np.float64)
    delta = np.array([], np.float64)
    template = np.zeros(64, np.float64)
    
    project = 19
    id_block = "78"
    channel = "1"
    points = 3
    nnodos = 20
    
    output = mp.Queue()
     
    nodos = __select_nodes(project, id_block, channel, nnodos)
    processes = []
     
    #serial(dbconn, nodos, output)
     
    for i in range(nnodos):
        processes.append(mp.Process(target=clustering, args=(nodos[i], points, output)))
     
    for p in processes:
        p.start()
     
    for p in processes:
        p.join(4)
     
    results = [output.get() for p in processes]
     
    templates = []
    ids = []
    for x in results:
        for y in x[0]:
            templates.append(y)
        for y in x[1]:
            ids.append(y)
     
    features_ids = insertFeaturesTemplate(templates, ids)
    
    features_ids = np.array(features_ids, np.float64)
     
    nspikes = len(features_ids)
    rho = np.empty(nspikes)
    delta = np.empty(nspikes)
    id_spikes = np.empty(nspikes)
    cluster_index = np.empty(len(features_ids))
    dc = libcd.getDC(connect, features_ids, id_spikes, len(features_ids), np.float(2.0), points)
    libcd.dpClustering(features_ids, len(features_ids), dc, points, "gaussian", id_spikes, cluster_index, rho, delta)
     
    
    res = neurodb.features.getFromDB(features_ids, "extra")
    neurodb.features.removeOnDB(features_ids)
    
    n = len(features_ids)
    max = rho.max()
    max = int(max*0.06)
    print max
    for j in range(len(delta)):
        if (rho[j] < max):
            delta[j] = 0
     
    coeficientes1, stats1= np.polynomial.polynomial.polyfit(rho, delta, 1, full=True)
     
    ajuste1 = ajuste(rho, coeficientes1)
    desvio1 = (stats1[0][0]/float(n))**0.5
     
    plt.plot(rho, delta, 'bo')
    plt.plot(rho, ajuste1, 'r')
    plt.plot(rho, ajuste1 + 1.4*desvio1, 'g')
    plt.show()
    
    pass    
