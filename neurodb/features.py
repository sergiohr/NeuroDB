'''
Created on Aug 4, 2015

@author: sergio
'''

import neurodb
import neurodb.neodb
import neurodb.config as config
import neodb.core
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import db
import scipy.signal as signal



def updateChannelFeatures(id_block, channel):
    #TODO: Create p1, p2 y p3 columns
    if db.NDB == None:
        db.connect()
        
    spikes = neodb.core.spikedb.get_from_db(db.NDB, id_block, channel)
    mspikes = []
    
    for spike in spikes:
        #mspikes.append(spike.waveform)
        #max = spike.waveform.max()
        #spike.waveform = spike.waveform/max
        spike.waveform = np.convolve(spike.waveform, np.ones((10,))/10, mode='same')
        mspikes.append((spike.waveform - np.mean(spike.waveform, 0)) / np.std(spike.waveform, 0))
    mspikes = np.array(mspikes)
    
    if mspikes == []:
        raise StandardError("Session %s, channel %s have not got spikes.")
    
    pca = PCA(n_components=10)
    transf = pca.fit_transform(mspikes)
    
    spikes_id = neodb.core.spikedb.get_ids_from_db(db.NDB, id_block, channel)
    
    #TODO: independizar esta parte de querys a la base
    cursor = db.NDB.cursor()
    i = 0
    for p in transf:
        id = spikes_id[i]
        neodb.core.spikedb.update(db.NDB, id = id, p1 = p[0], p2 = p[1], p3 = p[2], p4 = p[3], p5 = p[4], p6 = p[5], p7 = p[6], p8 = p[7], p9 = p[8], p10 = p[9])
        query = """SELECT UPSERT_FEATURES('%s', '%s','%s', '%s','%s', 
                          '%s','%s', '%s','%s', '%s', '%s')"""%(id, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])
        cursor.execute(query)
        db.NDB.commit()
        
        i = i+1

def getFeaturesFromSpikes(spikes, connection=None):
    
    if connection == None:
        if db.NDB == None:
            db.connect()
        cursor = db.NDB.cursor()
    else:
        cursor = connection.cursor()
    
    p = ""
    for i in spikes:
        p = p + " id_spike=%s or"%(i)
    p = p[:len(p)-3]
    
    query = "SELECT id, id_spike from FEATURES WHERE" + p
    
    cursor.execute(query)
    
    results = cursor.fetchall()
    #results = [x[0] for x in results]
    out = []
    
    for i in spikes:
        for j in range(len(results)):
            if i == results[j][1]:
                out.append(results[j][0])
    
    return np.array(out, np.float64)


def getFromDB(features_id, column):
    
    if db.NDB == None:
        db.connect()
    
    cursor = db.NDB.cursor()
    if column not in ["extra", "label"]:
        raise StandardError("""Parameter %s do not belong to table Features.""")%column
    
    p=""
    for id in features_id:
        p = p + " id=%s or"%(id)
    p = p[:len(p)-3]
    
    query = "SELECT id, %s from features where %s"%(column, p)
    
    cursor.execute(query)
    results = cursor.fetchall()
    out = []
    
    if column == 'extra':
        results = [(x[0],np.frombuffer(x[1], np.float32)) for x in results]
    
    for i in features_id:
        for j in range(len(results)):
            if i == results[j][0]:
                out.append(results[j])
    
    return out

def removeOnDB(features_id):
    
    if db.NDB == None:
        db.connect()
    
    p=""
    for id in features_id:
        p = p + " id=%s or"%(id)
    p = p[:len(p)-3]
    
    cursor = db.NDB.cursor()
    query = """DELETE FROM features WHERE %s"""%(p)
    
    cursor.execute(query)
    db.NDB.commit()
    
if __name__ == '__main__':
    pass