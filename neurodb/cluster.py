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
from mpl_toolkits.mplot3d import Axes3D

output = mp.Queue()

def compare_array(a, b):
    for i in range(len(a)):
        if a[i] != b[i]:
            print a[i], b[i]
            return False
    print "iguales"
    return True

def show_features(nodo, index, centers = None):
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
    
    if centers != None:
        qcolor = ['red', 'blue', 'green', 'black', 'yellow', 'white']
        k = 0
        for c in centers:
            
            query = """select p1, p2, p3 from features where id=%s"""%(nodo[c])
            cursor.execute(query)
            results = cursor.fetchall()
            
            x = []
            y = []
            z = []
            
            #for i in range(len(results)):
            x.append(results[0][0])
            y.append(results[0][1])
            z.append(results[0][2])
            
            #print "c:%s p1:%s p2:%s p3:%s"%(nodo[c], results[0][0], results[0][1], results[0][2])
                
            ax.scatter(x, y, z, s=200, marker='o', color=qcolor[k])
            ax.text(results[0][0],results[0][1],results[0][2],str(c))
            k=k+1
    
    plt.show()


def ajuste(local_density, coeficientes):
    vajuste = np.zeros(len(local_density))
    for j in range(len(local_density)):
        vajuste[j] = np.polynomial.polynomial.polyval(local_density[j], coeficientes)
        
    return vajuste

def show_selection(rho, delta, plot = True):
    n = len(rho)
    
    max = rho.max()
    max = int(max*0.1)
    deltacp = np.copy(delta)
    
    #pmean = deltacp.mean()
    pmean = 0
    for i in delta:
        pmean = pmean + i
    pmean = pmean/n;
    
    #print "mean:", pmean
    for j in range(len(deltacp)):
        if (rho[j] < max):
            deltacp[j] = pmean
    
    argmax = deltacp.argmax()
    max = deltacp[argmax]
    
    deltacp[argmax] = max/2
    
    coeficientes1, stats1= np.polynomial.polynomial.polyfit(rho, deltacp, 1, full=True)
    
    vajuste = np.zeros(len(rho))
    for j in range(len(rho)):
        vajuste[j] = np.polynomial.polynomial.polyval(rho[j], coeficientes1)
    ajuste1 = vajuste
    desvio1 = (stats1[0][0]/float(n))**0.5
    
    deltacp[argmax] = max;
    
    #print "ajuste1: m:%s b:%s sd:%s"%(coeficientes1[1], coeficientes1[0], desvio1)
    
    deltacp = np.copy(delta)
    y1 = deltacp[rho.argmin()]
    x1 = rho.min()
    y2 = 0
    x2 = rho.max()*0.1

    coeficientes1 = [-x1*(y2-y1)/(x2-x1) + y1,(y2-y1)/(x2-x1)]
    ajuste2 = ajuste(rho, coeficientes1)
    
    #print "ajuste2: m:%s b:%s sd:%s"%(coeficientes1[1], coeficientes1[0], desvio1)
    
    centers = []
    for i in range(len(rho)):
        if((delta[i] > ajuste1[i] + 2*desvio1) and (delta[i] > ajuste2[i] + 2*desvio1)):
            centers.append(i)
    
    if plot:
        plt.plot(rho, deltacp, 'bo')
        plt.plot(rho, ajuste1, 'r')
        plt.plot(rho, ajuste1 + 2*desvio1, 'g')
        plt.plot(rho, ajuste2 + 2*desvio1, 'g')
        plt.show()
    
    return centers

class DPClustering():
    def __init__(self, points=3, percentage_dc=1.8, kernel="gaussian", threading = "multi", nnodos = 4):
        if threading not in ["multi", "serial"]:
            raise StandardError("""Parameter threading must be contains 'multi' or 'serial'.""")
        
        self.connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
        
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
                if self.nnodos == 1:
                    spike_ids, labels = self.__process_serial(spike_ids)
                    #Lo que entra no es lo que sale de esta funcion, corregir
                    
                    
                    
                    return labels
                else:
                    results = self.__process_serial(spike_ids)
            
        if results != []:
            templates = []
            ids = []
            for x in results:
                templates.append(x[0])
                ids.append(x[1])
            
            smod = np.float(2)
             
            features_ids = self.__insertFeaturesTemplate(templates, ids)
            
            features_ids = np.array(features_ids, np.float64)
     
            nspikes = len(features_ids) 
            rho = np.empty(nspikes)
            delta = np.empty(nspikes)
            id_spikes = np.empty(nspikes)
            cluster_index = np.empty(len(features_ids))
            dc = libcd.getDC(self.connect, features_ids, id_spikes, len(features_ids), np.float(2.0), self.points)
            libcd.dpClustering(features_ids, len(features_ids), dc, self.points, "gaussian", id_spikes, cluster_index, rho, delta, smod)
            #cent = show_selection(rho, delta, plot=False)
            #show_features(features_ids, np.ones(len(features_ids)), cent)
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
        self.__saveLabelsMulti(spike_ids, labels)
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
     
        results = [output.get() for p in process]
        
        out=[]
        for r in results:
            for t in r:
                out.append(t)
        
        for p in process:
            p.join()
        
        return out
    
    def __process_serial(self, spikes):
        output = mp.Queue()
        
        nodos = self.__select_nodes(spikes)
        
        results = []
        if (self.nnodos == 1):
            spikes_id, labels = self.__clustering(spikes, self.points, output)
            return spikes_id, labels
            
        for nodo in nodos:
            self.__clustering(nodo, self.points, output)
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
        smod = np.float(2.5)
        
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
        libcd.dpClustering(features, nspikes, dc, points, "gaussian", spikes_id, cluster_index, rho, delta, smod)
        #plt.plot(delta[rho.argsort()])
        #plt.show()
        #show_selection(rho, delta)
        #show_features(features, cluster_index)
        
        if (self.nnodos == 1):
            return spikes_id, cluster_index
        
        #plt.plot(rho, delta, 'o')
        #plt.show()
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
        
        if (len(templates) < 10):
            raise StandardError("The amount of templates is not enough for calculating PCA. Templates: %s"%(len(templates)))
        
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
    
    def __saveLabelsMulti(self, spikes, labels):
        
        process = []
        nn = int(len(spikes)/10)
        
        for i in range(9):
            #print i*nn,i*nn+nn-1
            process.append(mp.Process(target=self.__saveLabels, args=(spikes[i*nn:i*nn+nn-1], labels[i*nn:i*nn+nn-1])))
        
        #print 9*nn,len(spikes)-1
        process.append(mp.Process(target=self.__saveLabels, args=(spikes[9*nn:len(spikes)-1], labels[9*nn:len(spikes)-1])))
        
        for p in process:
            p.start()
     
        for p in process:
            p.join()
        
    
    def __saveLabels(self, spikes, labels):
        username = 'postgres'
        password = 'postgres'
        host = '172.16.162.128'
        dbname = 'demo'
        dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
        cursor = dbconn.cursor()
        
        for i in range(len(spikes)):
            query = "UPDATE features SET label=%s where id_spike=%s"%(labels[i],spikes[i])
            cursor.execute(query)
        
        dbconn.commit()
        
if __name__ == '__main__':
    connect = "dbname=demo host=172.16.162.128 user=postgres password=postgres"
    id_project = 19
    #id_session = "84" #5768 spikes
    id_session = "94" #74394 spikes
    #id_session = "98" #2800 spikes
    channel = "1"
    points = 3
    n_nodos = 30
    
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
    
    np.set_printoptions(threshold=np.nan)
    dp = DPClustering(points=points, percentage_dc=2, kernel="gaussian", threading = "multi", nnodos = n_nodos)
    labels = dp.fitSpikes(spikes)
    
    #print labels
#     for i in range(0, int(labels.max())+1):
#         count = 0
#         template = np.zeros(64, np.float64)
#         plt.subplot(1,int(labels.max())+1,i+1)
#         for j in range(len(spikes)):    
#             if labels[j] == i:
#                 spike = neurodb.neodb.core.spikedb.get_from_db(db.NDB, id = int(spikes[j]))
#                 signal = spike[0].waveform
#                 template = template + signal
#                 plt.plot(signal, 'b')
#                 count = count + 1
#         if count != 0:
#             plt.plot(template/count, 'r')
#         plt.title("Cluster " + str(i) + ": # " + str(count))
#          
#     plt.show()
#     
#     pass