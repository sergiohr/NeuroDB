'''
Created on Dec 4, 2015

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



username = 'postgres'
password = 'postgres'
host = '172.16.162.128'
dbname = 'demo'

connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
cursor = connection.cursor()

id_project = 19
id_session = "94" #74394 spikes
channel = "1"
points = 3
n_nodos = 20

query = """select id_spike, label from features"""

f = file("spikes.bin","rb")
spikesc = np.load(f)
f.close()

f = file("labels.bin","rb")
labelsc = np.load(f)
f.close()

cursor.execute(query)
results = cursor.fetchall()

spikes = [x[0] for x in results]
labels = [x[1] for x in results]

#labelsc = np.array(labelsc)
#spikesc = np.array(spikesc)

error = 0
print len(labelsc)
for i in range(len(labelsc)):
    index = np.argwhere(spikesc==spikes[i])
    if labelsc[i] != labels[index[0][0]]:
        error = error + 1

print error
            