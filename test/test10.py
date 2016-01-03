'''
Created on Dec 3, 2015

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
import neurodb.features
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

def show_features(nodo, index):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    
    connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    cursor = connection.cursor()
    
    qcolor = ['red', 'blue', 'green', 'black', 'yellow', 'white']
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for k in np.unique(index):
        subnodo = []
        for q in range(len(nodo)):
            if index[q] == k:
                subnodo.append(nodo[q])
        
        query = """select p1, p2, p3 from features where """
        condition = ""
        for f in subnodo:
            condition = condition + "id=%s or "%(f)
        condition = condition[:len(condition)-5]
        query = query + condition
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        x = []
        y = []
        z = []
        
        for i in results:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        
        ax.scatter(x, y, z, color=qcolor[int(k)])
        
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
    
    plt.show()

def show_spikes(spikes):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    
    connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))

    for j in range(len(spikes)):    
        spike = neurodb.neodb.core.spikedb.get_from_db(connection, id = int(spikes[j]))
        signal = spike[0].waveform
        plt.plot(signal)
    
    plt.show()

def show_spikes_label(spikes, labels, label, limit):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    
    connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    k = 0
    for j in range(len(spikes)):
        if (labels[j] == label) and (k < limit):
            spike = neurodb.neodb.core.spikedb.get_from_db(connection, id = int(spikes[j]))
            signal = spike[0].waveform
            plt.plot(signal)
            k = k + 1
    
    plt.show()

if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    
    connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    cursor = connection.cursor()
    

# VER FEATURES

    query = """ select features.id from features join spike
                on features.id_spike = spike.id
                where spike.id_segment = 260 and spike.index < 6801038"""
    
#     query = """ select features.id from features join spike
#                 on features.id_spike = spike.id
#                 where spike.id_segment = 260 and spike.index > 6801038 and spike.index < 13602000"""

#     query = """ select features.id from features join spike
#                 on features.id_spike = spike.id
#                 where spike.id_segment = 260 and spike.index > 13602000"""

    #cursor.execute(query)
    #results = cursor.fetchall()
    
    #nodo = [x[0] for x in results]
    #print len(nodo)
    #show_features(nodo, np.ones(len(nodo)))
    
#     query = "UPDATE features SET label = 3 where id in ("+ query + ")"
# #     
#     cursor.execute(query)
#     connection.commit()

# VER SPIKES
    
    query = """ select id_spike from features where label = 3 limit 100"""    
    cursor.execute(query)
    results = cursor.fetchall()
    nodo = [x[0] for x in results]
    show_spikes(nodo)

# VER CLUSTERIZACION

    f = file("spikes.bin","rb")
    spikes = np.load(f)
    f.close()
    
    f = file("labels.bin","rb")
    labels = np.load(f)
    f.close()
    
    show_spikes_label(spikes, labels, 3, 100)
    
    pass