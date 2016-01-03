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


def show(connection, id):
    spike = neurodb.neodb.core.spikedb.get_from_db(connection,id=id)
    signal = spike[0].waveform
    plt.plot(signal)
    plt.show()


username = 'postgres'
password = 'postgres'
host = '172.16.162.128'
dbname = 'demo'

connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
cursor = connection.cursor()

id_project = 19
id_session = "94" #74394 spikes
#id_session = "98" #2800 spikes
channel = "1"
points = 3
n_nodos = 20

project = neurodb.project.get_from_db(id_project)
session = project.get_session(int(id_session))
channels = session.get_channels()

for ch in channels:
    if ch['channel']==int(channel):
        rc = session.get_channel(ch['id'])

spikes = rc.get_spikes()

dp = neurodb.cluster.DPClustering(points=points, percentage_dc=2, kernel="gaussian", threading = "multi", nnodos = n_nodos)
labels = dp.fitSpikes(spikes)



############################
query = """
select features.id_spike, features.label from features 
join spike on spike.id = features.id_spike 
join segment on segment.id = spike.id_segment 
where segment.id_block = %s"""%(id_session)
 
cursor.execute(query)
results = cursor.fetchall()
 
spikesB = [x[0] for x in results]
labelsB = [x[1] for x in results]

f = file("spikes_id_94.bin","rb")
spikesA = np.load(f)
f.close()

f = file("labels_id_94.bin","rb")
labelsA = np.load(f)
f.close()



error = 0
for i in range(len(labelsA)):
    index = np.argwhere(spikesB==spikesA[i])
    if labelsA[i] == 1:
        if labelsB[index[0][0]] != 1:
            error = error + 1
            
    if labelsA[i] == 2:
        if labelsB[index[0][0]] != 3:
            error = error + 1
    
    if labelsA[i] == 3:
        if labelsB[index[0][0]] != 2:
            error = error + 1
            
print error