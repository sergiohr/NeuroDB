'''
Created on Dec 13, 2015

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
import neurodb.cluster
import random
from sklearn.cluster import KMeans, AgglomerativeClustering, MiniBatchKMeans
from neurodb.cfsfdp import libcd#
import multiprocessing as mp
import neurodb.features
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
import time

def show(connection, id):
    spike = neurodb.neodb.core.spikedb.get_from_db(connection,id=id)
    signal = spike[0].waveform
    plt.plot(signal)
    plt.show()

def run(n_nodos = 20):
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    
    connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    cursor = connection.cursor()
    
    id_project = 19
    id_session = "117" #74394 spikes
    #id_session = "98" #2800 spikes
    channel = "1"
    points = 3
    
    project = neurodb.project.get_from_db(id_project)
    session = project.get_session(int(id_session))
    channels = session.get_channels()
    
    for ch in channels:
        if ch['channel']==int(channel):
            rc = session.get_channel(ch['id'])
    
    spikes = rc.get_spikes()
    
    t1 = time.time()
    
    dp = neurodb.cluster.DPClustering(points=points, percentage_dc=2, kernel="gaussian", threading = "serial", nnodos = n_nodos)
    labels = dp.fitSpikes(spikes)
    
    t2 = time.time()
    
    print (t2-t1)/60
    
    ############################
    query = """
    select features.id_spike, features.label from features 
    join spike on spike.id = features.id_spike 
    join segment on segment.id = spike.id_segment 
    where segment.id_block = %s"""%(id_session)
     
    cursor.execute(query)
    results = cursor.fetchall()
     
    spikesB = np.array([x[0] for x in results])
    labelsB = np.array([x[1] for x in results])
    
    query = """
    select features.id_spike, features.labelPrueba from features 
    join spike on spike.id = features.id_spike 
    join segment on segment.id = spike.id_segment 
    where segment.id_block = %s"""%(id_session)
    
    cursor.execute(query)
    results = cursor.fetchall()
     
    spikesA = np.array([x[0] for x in results])
    labelsA = np.array([x[1] for x in results])
    
    query = """select distinct features.label from features 
                join spike on spike.id = features.id_spike 
                join segment on segment.id = spike.id_segment 
                where segment.id_block=117"""
    cursor.execute(query)
    results = cursor.fetchall()
    clusters = np.array([x[0] for x in results])
    
    print "Clusters: ", clusters
    
    lb1 = 0
    lb2 = 0
    lb3 = 0
    
    for i in clusters:
        query = """select count(features.label) from features 
        join spike on spike.id = features.id_spike 
        join segment on segment.id = spike.id_segment 
        where segment.id_block=%s and labelprueba=1 and label=%s;"""%(id_session, i)
        cursor.execute(query)
        results = cursor.fetchall()
        if lb1 < results[0][0]:
            lb1 = results[0][0]
            index1 = i
        
        query = """select count(features.label) from features 
        join spike on spike.id = features.id_spike 
        join segment on segment.id = spike.id_segment 
        where segment.id_block=%s and labelprueba=2 and label=%s;"""%(id_session, i)
        cursor.execute(query)
        results = cursor.fetchall()
        if lb2 < results[0][0]:
            lb2 = results[0][0]
            index2 = i
            
        query = """select count(features.label) from features 
        join spike on spike.id = features.id_spike 
        join segment on segment.id = spike.id_segment 
        where segment.id_block=%s and labelprueba=3 and label=%s;"""%(id_session, i)
        cursor.execute(query)
        results = cursor.fetchall()
        if lb3 < results[0][0]:
            lb3 = results[0][0]
            index3 = i
    
    error = 90000-lb1-lb2-lb3
    
    #print (t2-t1)/60            
    print "error:",error
    print "lb1:",lb1
    print "lb2:",lb2
    print "lb3:",lb3
    connection.close()

for k in range(10):
    print "--- %s ---"%(k)
    run(20)