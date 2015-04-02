'''
Created on Dec 21, 2013

@author: Sergio Hinojosa
'''
from neo import io
import numpy as np
import os
import re
import pickle
import ConfigParser
import quantities



CONFIG_FILE = 'neurodb.conf'

def save_data(conf_name, conf_value):
    conf = None
    try:
        f = open(CONFIG_FILE, 'r')
        conf = pickle.load(f)
        f.close()
    except Exception as e:
        print "Could not save file. New conf file created ", e
        conf = {}
    
    conf[conf_name] = conf_value
    
    f = open(CONFIG_FILE, 'w')
    pickle.dump(conf, f)
    f.close()

def read_data(conf_name, default):
    
    try:
        f = open(CONFIG_FILE, 'r')
        conf = pickle.load(f)
        f.close()
    except Exception as e:
        print "Could not read file. Defaults used. ", e
        return default
    
    if conf_name in conf:
        return conf[conf_name]
    else:
        return default

def read_segments(path = None, trialname = None, channels = None, dtype='i2', sampling_rate=14400):
    """Build segment where each channel is formed from several files"""
    register_dir = read_data('register_dir', '/home/sergio/workspace_oss/WebUI/registers')
    files = os.listdir(register_dir)
    files_p = []
    for file in files:
        regex = trialname + "_\w+_\d+"
        match = re.match(regex,file)
        if match:
            files_p.append(file)
    
    for file in files_p:
        file = register_dir + '/' + file
        segment = io.RawBinarySignalIO( filename = file).read_segment(sampling_rate=sampling_rate,dtype=dtype,nbchannel=channels)
        channel = segment.analogsignals[0]
        channel = np.array(channel)/float(channel[0])
    pass

def get_quantitie(unit):
    if unit not in ['V', 'v', 'mV', 'mv', 'uV', 'uv']:
        raise StandardError("Parameter must be 'V' , 'mV' or 'uV'")
    
    if unit == 'V' or unit == 'v':
        return quantities.V
    if unit == 'mV' or unit == 'mv':
        return quantities.mV
    if unit == 'uV' or unit == 'uv':
        return quantities.uV

def last_file(path):
    """Returns the last modified file in a path."""
    name = None
    file_path = None
    if os.path.isdir(path):
        files = []
        for name in os.listdir(path):
            dir = os.path.join(path, name)
            if os.path.isfile(dir):  # solo archivos
                if name[0] not in ['~', '.']:
                    files.append((os.path.getmtime(dir), name, dir))
        # Ultimo archivo modificado
        if files != []:
            name, file_path = sorted(files)[-1][1:3]
        
    return name, file_path


if __name__ == '__main__':
    d = '/home/sergio/iibm/sandbox'
#     save_data('register_dir', d)
#     read_segments(trialname='030712',channels=25)
    files = []
    while(1):
        name, path = last_file(d)
        if name not in files:
            print name, path
            files.append(name) 
    pass
