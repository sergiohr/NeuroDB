'''
Created on Feb 10, 2015

@author: sergio
'''

import numpy as np
import ctypes
import numpy.ctypeslib as npct
import matplotlib.pyplot as plt
import psycopg2

import neodb.core
username = 'postgres'
password = 'postgres'
host = '192.168.2.2'
dbname = 'demo'
url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))

array_1d_double = npct.ndpointer(dtype=np.double, ndim=1, flags='CONTIGUOUS')

array_1d_int = npct.ndpointer(dtype=np.int64, ndim=1, flags='CONTIGUOUS')
array_2d_double = npct.ndpointer(dtype=np.double, ndim=2, flags='CONTIGUOUS')

libcd = npct.load_library("cfsfdp", "/home/sergio/Proyectos/NeuroDB/NeuroDB/NeuroDB/cfunctions/cfsfdp")

libcd.get_dc.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_float]
libcd.get_dc.restype = ctypes.c_float

libcd.get_n_dbspikes.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
libcd.get_n_dbspikes.restype = ctypes.c_int

libcd.get_cluster_dp2.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, array_1d_double, array_1d_double, ctypes.c_double]
libcd.get_cluster_dp2.restype = ctypes.c_int

connect = "dbname=demo host=192.168.2.2 user=postgres password=postgres"
id_block = "54"
channel = "3"

dc = libcd.get_dc(connect, id_block, channel, 2.0)
clusters_index = np.empty(1026)
spikes_id = np.empty(1026)

libcd.get_cluster_dp2(connect, id_block, channel, spikes_id, clusters_index, dc)

print libcd.get_n_dbspikes(connect, id_block, channel)

for i in range(int(clusters_index.max())+1):
    plt.subplot(int(clusters_index.max())+1,1,i+1)
    for j in range(1026):
        if clusters_index[j] == i:
            spikes = neodb.core.spikedb.get_from_db(dbconn, id_block = 54, channel = 3, id = int(spikes_id[j]))
            signal = spikes[0].waveform
            plt.plot(signal)

plt.show()

if __name__ == '__main__':
    pass