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

sr = 32258
file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/1p2s90000.mat'
name = file.split('/')[-1]

x = scipy.io.loadmat(file)
x = x['data'][0]

ndbdetector = Spike.Detector()
ndbdetector.set_parameters(sr=int(sr))
spikes, index, thr = ndbdetector.get_spikes(x)

pass