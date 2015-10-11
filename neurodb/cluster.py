'''
Created on Jul 16, 2015

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
import db
import multiprocessing as mp
import neurodb.features
from sklearn.decomposition import PCA

output = mp.Queue()



def get_centers(connect, nodo, points):
    centersT = []
    
    spikes_id = np.array(nodo, np.float64)
    nspikes = len(spikes_id)
    
    local_density = np.empty(nspikes)
    distance_to_higher_density = np.empty(nspikes)
    cluster_index = np.empty(nspikes)
    nneigh = np.empty(nspikes)
    centers = np.empty(nspikes)
    
    dc = libcd.get_dc(connect, spikes_id, nspikes, np.float(1.8), points)
    libcd.cluster_dp(connect, local_density, distance_to_higher_density, spikes_id, 
                     cluster_index, nneigh, centers, dc, points, nspikes, "gaussian")
    
    print "nodo procesado. ncenters:%s"%(int(centers[0]))
    
    ncenters = centers[0]
    
    for j in range(int(centers[0])):
        centersT.append([local_density[int(centers[j+1])], distance_to_higher_density[int(centers[j+1])]])
    
    return centersT, ncenters, cluster_index


class DPClustering():
    def __init__(self, points=3, percentage_dc=1.8, kernel="gaussian", threading = "multi", nnodos = 4):
        if threading not in ["multi", "serial"]:
            raise StandardError("""Parameter threading must be contains 'multi' or 'serial'.""")
        
        self.threading = threading
        self.points = points
        self.percentage_dc = percentage_dc
        self.kernel = kernel
        self.nnodos = nnodos
        
        
    def fitSpikes(self, spike_ids = None, recordingchannel_id = None):
        results = []
        spike_ids_cp = np.copy(spike_ids)
        if spike_ids != None :
            if self.threading == "multi":
                results = self.__process_multi(spike_ids)
            
            if self.threading == "serial":
                results = self.__process_serial(spike_ids)
            
        if results != []:
            templates = []
            ids = []
            for x in results:
                templates.append(x[0])
                ids.append(x[1])
             
            features_ids = self.__insertFeaturesTemplate(templates, ids)
            
            features_ids = np.array(features_ids, np.float64)
     
            nspikes = len(features_ids)
            rho = np.empty(nspikes)
            delta = np.empty(nspikes)
            id_spikes = np.empty(nspikes)
            cluster_index = np.empty(len(features_ids))
            dc = libcd.getDC(connect, features_ids, id_spikes, len(features_ids), np.float(2.0), points)
            libcd.dpClustering(features_ids, len(features_ids), dc, points, "gaussian", id_spikes, cluster_index, rho, delta)
            # Cuando se hace una consulta a la base no se devuelve los ids ordenados segun la consulta
            
        spikes = neurodb.features.getFromDB(features_id=features_ids, column='extra')
        
        labels = []
        for j in range(len(spike_ids_cp)):
            flag = 0
            for k in range(len(spikes)):
                if spike_ids_cp[j] in spikes[k][1]:
                    labels.append(cluster_index[k])
                    flag = 1
            if flag == 0:
                labels.append(0)
        
        neurodb.features.removeOnDB(features_id=features_ids)
        return np.array(labels)
    
    def __select_nodes(self, spikes):
        spikes_cp = list(spikes)
        random.shuffle(spikes_cp)
        
        len_spikes = len(spikes_cp)
        len_nodo = np.ceil(float(len_spikes)/float(self.nnodos))
        
        nodos = []
        
        for i in range(self.nnodos):
            nodo = []
            j = 0
            while(spikes_cp != [] and j<len_nodo):
                nodo.append(spikes_cp.pop())
                j = j + 1
                
            nodos.append(nodo)
        
        return nodos
    
    def __process_multi(self, spikes):
        output = mp.Queue()
        
        nodos = self.__select_nodes(spikes)
        
        process = []
        
        for i in range(self.nnodos):
            process.append(mp.Process(target=self.__clustering, args=(nodos[i], self.points, output)))
            
        for p in process:
            p.start()
     
        for p in process:
            p.join(0.5)
        
        results = [output.get() for p in process]
        
        out=[]
        for r in results:
            for t in r:
                out.append(t)
        
        return out
    
    def __process_serial(self, spikes):
        output = mp.Queue()
        
        nodos = self.__select_nodes(spikes)
        
        results = []
        for nodo in nodos:
            self.__clustering(nodo, 3, output)
            result = output.get()
            results.append(result)
        
        
        out=[]
        for r in results:
            for t in r:
                out.append(t)
        
        return out
        
    def __clustering(self, nodo, points, output):
        username = 'postgres'
        password = 'postgres'
        host = '172.16.162.128'
        dbname = 'demo'
        url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
        dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
        
        connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
        spikes_id = np.array(nodo, np.float64)
        
        nspikes = len(nodo)
        
        rho = np.empty(nspikes)
        delta = np.empty(nspikes)
        nneigh = np.empty(nspikes)
        centers = np.empty(nspikes)
        
        cluster_index = np.empty(nspikes)
        features = neurodb.features.getFeaturesFromSpikes(nodo, connection=dbconn)
        
        dc = libcd.getDC(connect, features, spikes_id, nspikes, np.float(1.8), points)
        
        libcd.dpClustering(features, nspikes, dc, points, "gaussian", spikes_id, cluster_index, rho, delta)
        
        plt.plot(rho, delta, 'o')
        plt.show()
        templates = []
        spikes = []
        out = []
        
        for i in range(1, int(cluster_index.max())+1):
            template = np.zeros(64, np.float64)
            gspikes = []
            k = 0
            for j in range(nspikes):
                if cluster_index[j] == i:
                    spike = neurodb.neodb.core.spikedb.get_from_db(dbconn, id = int(spikes_id[j]))
                    signal = spike[0].waveform
                    template = template + signal
                    gspikes.append(spikes_id[j])
                    k = k + 1
            template = template/k
            out.append((template, gspikes))
        
        output.put(out)
        
    def __insertFeaturesTemplate(self, templates, spike_ids):
        username = 'postgres'
        password = 'postgres'
        host = '172.16.162.128'
        dbname = 'demo'
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
        
if __name__ == '__main__':
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_project = 19
    id_session = "78"
    channel = "1"
    points = 3
    n_nodos = 1
    
    if db.NDB == None:
        db.connect()
    
    color = ['bo', 'ro', 'go', 'co', 'ko', 'mo', 'b^', 'r^', 'g^', 'c^', 'k^', 'm^']
    centers = []
    rho = np.array([], np.float64)
    delta = np.array([], np.float64)
    ncenters = 0
    
    project = neurodb.project.get_from_db(id_project)
    session = project.get_session(int(id_session))
    channels = session.get_channels()
    
    for ch in channels:
        if ch['channel']==int(channel):
            rc = session.get_channel(ch['id'])
    
    spikes = rc.get_spikes()
    
    dp = DPClustering(points=3, percentage_dc=1.8, kernel="gaussian", threading = "serial", nnodos = n_nodos)
    labels = dp.fitSpikes(spikes)
    print labels
    for i in range(0, int(labels.max())+1):
        count = 0
        template = np.zeros(64, np.float64)
        plt.subplot(int(labels.max())+1,1,i+1)
        for j in range(len(spikes)):    
            if labels[j] == i:
                spike = neurodb.neodb.core.spikedb.get_from_db(db.NDB, id = int(spikes[j]))
                signal = spike[0].waveform
                template = template + signal
                plt.plot(signal, 'b')
                count = count + 1
        plt.plot(template/count, 'r')
        plt.title(str(i) + " " + str(count))
    plt.show()
    
    pass