'''
Created on Dec 20, 2015

@author: sergio
'''

import scipy.io
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
import neurodb.Spike.spike as Spike

def show(signal):
    plt.plot(signal)
    plt.show()

username = 'postgres'
password = 'postgres'
host = '172.16.162.128'
dbname = 'demo'
channel = 1
id_block = 117

dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))

neurodb.project.ls()

p = neurodb.project.get_from_db(19)

b = p.get_session(118)
c = b.get_channel(279)
s = c.ls_spikes()

sp = c.get_spike(s[0])
signal = sp.waveform
plt.plot(signal)

sp = c.get_spike(s[30000])
signal = sp.waveform
plt.plot(signal)

sp = c.get_spike(s[30000-1])
signal = sp.waveform
plt.plot(signal)

plt.show()

pass

# spikes = neurodb.neodb.core.spikedb.get_from_db(dbconn, id_block = id_block, channel = channel, id = int()
# signal = spikes[0].waveform
# show(signal)

pass