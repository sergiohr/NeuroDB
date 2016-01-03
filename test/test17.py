'''
Created on Apr 20, 2015

@author: sergio
'''
import scipy.io
import numpy as np
import neurodb.neodb.core
import neurodb
import quantities

if __name__ == '__main__':
    x = scipy.io.loadmat('/home/sergio/matlab/extra/NeuroCube/mat/Spikesim.mat')
    x = x['data'][0]
    id_block = 57
    index = 56
    
    
    connection = neurodb.db.NDB
    
    #project = neurodb.project.create('proyectoTest', '4/6/2015', 'proyecto de prueba')
    
    
    
    rc = neurodb.neodb.core.RecordingChannelDB(id_block = id_block, index = index)
    rc.save(connection)
          
    sg = neurodb.neodb.core.SegmentDB(id_block = id_block, index = 0, 
                                      file_origin = 'segment%s'%(rc.index), 
                                      name='segment%s'%(rc.index))
    sg.save(connection)
          
    an = neurodb.neodb.core.AnalogSignalDB(id_segment = sg.id, id_recordingchannel = rc.id, 
                                           signal=x, channel_index = index, units = 'V', 
                                           sampling_rate=32258*quantities.Hz,
                                           t_start = 0.0, name='signal%s'%(rc.index),
                                           index = 0)
#     
    an.save(connection)
        
    neurodb.project.save_channel_spikes(57, channel=index)
    neurodb.project.update_spike_coordenates(id_block=57, channel=index)
    
    
    
    pass