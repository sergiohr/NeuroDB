'''
Created on Jun 4, 2015
oh
@author: sergio
'''

import scipy.io
import numpy as np
import neurodb.neodb.core
import neurodb
import neurodb.features 
import quantities


if __name__ == '__main__':
    #file = '/home/sergio/matlab/extra/NeuroCube/mat/sims/Spikesim.mat'
    #file = '/home/sergio/Proyectos/sandbox/datatest.mat'
    #file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/1p2s90000.mat'
    #file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/spikes90000.mat'
    
    print "#########"
    print "1s2p5sp90000.mat"
    file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/1s2p5sp90000.mat'
    name = file.split('/')[-1]
    #neurodb.project.update_spike_coordenates(76, 1)
   
    project = neurodb.project.get_from_db(19)
       
    sr = 32258
       
    id_session = project.add_session(id_individual=15, date='06/04/2016', name='ruido1/2.5',
                                      session_path=file, description='test DP', 
                                      sample_rate=sr, dtype='float16', unit='V', 
                                      scale_factor=None, nchannels=1, mode='Matlab')
    print "id session: ",id_session
    
    neurodb.features.updateChannelFeatures(id_session, 1)

    #################################
    
    print "#########"
    print "1s2sp90000.mat"
    file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/1s2sp90000.mat'
    name = file.split('/')[-1]
    #neurodb.project.update_spike_coordenates(76, 1)
   
    project = neurodb.project.get_from_db(19)
       
    sr = 32258
       
    id_session = project.add_session(id_individual=15, date='06/04/2016', name='ruido1/2',
                                      session_path=file, description='test DP', 
                                      sample_rate=sr, dtype='float16', unit='V', 
                                      scale_factor=None, nchannels=1, mode='Matlab')
    print "id session: ",id_session
    
    neurodb.features.updateChannelFeatures(id_session, 1)

    #################################
    
    print "#########"
    print "1s1p5sp90000.mat"
    file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/1s1p5sp90000.mat'
    name = file.split('/')[-1]
    #neurodb.project.update_spike_coordenates(76, 1)
   
    project = neurodb.project.get_from_db(19)
       
    sr = 32258
       
    id_session = project.add_session(id_individual=15, date='06/04/2016', name='ruido1/1.5',
                                      session_path=file, description='test DP', 
                                      sample_rate=sr, dtype='float16', unit='V', 
                                      scale_factor=None, nchannels=1, mode='Matlab')
    print "id session: ",id_session
    
    neurodb.features.updateChannelFeatures(id_session, 1)
    
    #################################
    
    print "#########"
    print "1s1p2sp90000.mat"
    file = '/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/1s1p2sp90000.mat'
    name = file.split('/')[-1]
    #neurodb.project.update_spike_coordenates(76, 1)
   
    project = neurodb.project.get_from_db(19)
       
    sr = 32258
       
    id_session = project.add_session(id_individual=15, date='06/04/2016', name='ruido1/1.2',
                                      session_path=file, description='test DP', 
                                      sample_rate=sr, dtype='float16', unit='V', 
                                      scale_factor=None, nchannels=1, mode='Matlab')
    print "id session: ",id_session
    
    neurodb.features.updateChannelFeatures(id_session, 1)

    pass