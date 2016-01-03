'''
Created on Dec 20, 2015

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

query = """
select features.id_spike, features.label from features 
join spike on spike.id = features.id_spike 
join segment on segment.id = spike.id_segment 
where segment.id_block = 94
"""

cursor.execute(query)
results = cursor.fetchall()

spikes = np.array([x[0] for x in results])
labels = np.array([x[1] for x in results])

outfile = "spikes_id_94.bin"
f = file(outfile,"wb")
np.save(f, spikes)
f.close()

outfile = "labels_id_94.bin"
f = file(outfile,"wb")
np.save(f, labels)
f.close()
