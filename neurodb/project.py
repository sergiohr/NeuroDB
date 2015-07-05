'''
Created on Dec 22, 2013

@author: Sergio Hinojosa Rojas
'''

import neurodb
import neurodb.neodb
import neurodb.config as config
import neodb.core
import datetime
import neodb.dbutils
import os
import quantities
from neo import io
import utils
import re
import Spike.spike as Spike
import Spike.sorter as Sorter
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import db
import scipy.io


class Project(object):
    '''
    Project gather all information and registers about a project of experimental in a individual.
    '''
    def __init__(self, name = None, date = None, description = None, index = None):
        '''
        name : name of project (25 characters max.)
        date : date of start project. Format dd-mm-yyyy or dd/mm/yyy.
        description: aditional information (150 characters max.)
        index: number of internal reference.
        
        use:
        project = neodb.core.Project("project1", "19-05-2014", "Cognital analisys")
        '''
        self.id = None
        self.index = index
        self.name = name
        self.description = description
        
        if date:
            self.date = neodb.dbutils.get_ppgdate(date)
        else:
            self.date = date
        
        if db.NDB == None:
            db.connect()
            
        self.connection = db.NDB

    def save(self):
        '''
        Save Project into database trough connection. 'connection" is a Psycopg2 connection. You can get
        connection using neodb.connectdb().
        '''
        if self.name == None:
            raise StandardError("Project must have a name.")
        
        other = neodb.dbutils.get_id(self.connection, 'project', name = self.name)
        
        if other != []:
            raise StandardError("There is another project with name '%s'."%self.name)
        
        cursor = self.connection.cursor()
        query = """INSERT INTO project (name, date, description, index)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query,[self.name, self.date, self.description, self.index])
        self.connection.commit()
        
        [(id, _)] = neodb.dbutils.get_id(self.connection, 'project', name = self.name)
        
        return id
    
    def get_from_db(self, id):
        cursor = self.connection.cursor()
        query = """ SELECT * FROM project WHERE id = %s"""
        cursor.execute(query, [id])
        results = cursor.fetchall()
        
        if results != []:
            self.name =          results[0][2]
            self.description =   results[0][3]
            self.date =   results[0][4]
            self.id = results[0][0]
        
            results = {}
            results['name'] = self.name
            results['description'] = self.description
            results['date'] = self.date
            
            return results
        else:
            print "There are not a Project with id = %s"%id
            return None
    
    def ls_sessions(self):
        sessions = neodb.dbutils.get_id(db.NDB, 'block', id_project=self.id)
        for i in sessions:
            print "id:%s, name:%s"%(i[0],i[1])
        return sessions
        
        
        pass

    def add_session(self, id_individual, date, name, session_path,
                    description = None, sample_rate = 14400, dtype = 'i2', 
                    unit = 'mv', scale_factor = 1, nchannels = 25, mode = None):
        """
        add_session(id_project, id_individual, date, name, session_path,
                    description = None, sample_rate = 14400, dtype = 'i2', 
                    unit = 'mv', scale_factor = 1)
        
        Saves the records of a session.
        
        Parameters:
        id_project (mandatory)
        id_individual (mandatory)
        date (mandatory)
        name (mandatory)
        session_path (mandatory)
        description
        sample_rate
        dtype
        unit
        scale_factor
        """
        #TODO: implement "scale factor" as the factor that adjusts the measured value 
        # for an electric interpretation with unit.
        # Add nchannel parameter to create a recordingchannels objects that gatter the
        # segments of analogsignals
        
        if type(date) == str:
            date = neodb.dbutils.get_datetimedate(date)
        elif type(date) != datetime.date:
            raise StandardError("Invalid date type. It must be 'datetime.date' or " + 
                                 "string with format 'dd-mm-yyyy' or 'dd/mm/yyyy'")
        
        if mode == 'Matlab':
            if not os.path.isfile(session_path):
                raise StandardError("Invalid file.")
        else:
            if not os.path.isdir(session_path):
                raise StandardError("Invalid path.")
        
        # create Session Block
        session = neodb.core.BlockDB(id_project = self.id,
                                     id_individual = id_individual, name = name, 
                                     rec_datetime = date, description = description)
        
        id_session = session.save(self.connection)
        
        if mode == None:
            carpeta = session_path
            archivos = []
            for nombre in os.listdir(carpeta):
                match = re.match('(^(.*)-(\d+)-(\d+)$)', nombre)
                if match:
                    direccion = os.path.join(carpeta, nombre)
                    if os.path.isfile(direccion):  # solo archivos
                        ndate = match.groups()[1]
                        index = int(match.groups()[3])
                        archivos.append((index, os.path.getmtime(direccion), nombre, direccion))
                        
            archivos.sort()
            
            # Create recordingchannels
            rchannels = []  
            for n in range(nchannels):
                rc = neodb.core.RecordingChannelDB(id_block = id_session, index = n)
                id_rc = rc.save(db.NDB)
                rchannels.append((n, id_rc))
            
            # Create segments
            tstart = 0.0
            tlength = 0.0
            
            for nindex, _, name, segmentfile_path in archivos:
                segmentdb = neodb.core.SegmentDB(id_session, name, file_origin = segmentfile_path)
                id_segment = segmentdb.save(db.NDB)
                
                segment = io.RawBinarySignalIO(filename = segmentfile_path).read_segment(sampling_rate = sample_rate,          
                                                                                     dtype = dtype,
                                                                                     nbchannel=nchannels, 
                                                                                     rangemin = -16380, 
                                                                                     rangemax = 16380)
                
                cindex = 0
                
                # Save analogsignals
                for channel in segment.analogsignals:
                    analogsignaldb = neodb.core.AnalogSignalDB(id_segment = id_segment,
                                                               id_recordingchannel =  rchannels[cindex][1],
                                                               name = name, 
                                                               signal = channel.tolist(), 
                                                               channel_index = rchannels[cindex][0],
                                                               units = utils.get_quantitie(unit),
                                                               file_origin = segmentfile_path,
                                                               sampling_rate = sample_rate*quantities.Hz,
                                                               t_start = tstart,
                                                               index = nindex)
                    analogsignaldb.save(self.connection)
                    cindex = cindex + 1
                
                tlength = len(channel)/sample_rate
                tstart = tstart + tlength
        
        if mode == 'Matlab':
            x = scipy.io.loadmat(session_path)
            x = x['data'][0]
            nchannels = 1
            
            name = session_path.split('/')[-1]
            
            rc = neurodb.neodb.core.RecordingChannelDB(id_block = id_session, index = nchannels)
            rc.save(self.connection)
            
            sg = neurodb.neodb.core.SegmentDB(id_block = id_session, index = nchannels, 
                                      file_origin = session_path, 
                                      name = name)
            sg.save(self.connection)
            
            an = neurodb.neodb.core.AnalogSignalDB(id_segment = sg.id, id_recordingchannel = rc.id, 
                                           signal=x, channel_index = nchannels, units = utils.get_quantitie(unit), 
                                           sampling_rate = sample_rate*quantities.Hz,
                                           t_start = 0.0, name = name,
                                           index = nchannels)
            
            an.save(self.connection)
            
            neurodb.project.save_channel_spikes(id_block=id_session, channel=nchannels)
            neurodb.project.update_spike_coordenates(id_block=id_session, channel=nchannels)
            
        
    def get_session(self, id):
        session = neodb.core.BlockDB()
        id_session = neodb.dbutils.get_id(self.connection, 'block', id_project = self.id, id=id)
        id_session = id_session[0][0]
        session.get_from_db(self.connection, id_session)
        
        return session
        
            

def ls():
    if db.NDB == None:
        db.connect()
    
    projects = neodb.dbutils.get_id(db.NDB, 'project')
    if projects != []:
        for i in projects:
            print "id:%s name:%s"%(i[0], i[1])
    else:
        print "There are not projects."

def create(name, date, description = None, projectcode = None):
    """create_project(name, date, description = None, projectcode = None)

       Creates project in database. Project may contains several individuals.

       Parameters
       name: Name of project. Mandatory.
       projectcode: Code of project. Number to identify the project. Optional
       description: Description or info about the project. Optional
       date: Date of creation. Mandatory.

       Return
       Function returns the id that identified it in database. Each project have 
       unique id.
       
       USE:
       
       project = create_project(name="Project1", description="Testing project", date="10/10/2014")
       """
    if db.NDB == None:
        db.connect()
    
    project = Project(name, date, description, projectcode)
    id = project.save()
    project.id = id
    
    print "Project created. Id: %s"%id
    return project

def find(name = None, date_from = None, date_end = None):
    if db.NDB == None:
        db.connect()
    
    projects =[]
    
    if name != None:
        projects = neodb.dbutils.get_id(db.NDB, 'project', name = name)
    else:
        if date_from != None and date_end != None:
            projects = neodb.dbutils.get_id(db.NDB, 'project',
                                       date_start = date_from,
                                       date_end = date_end)
        else:
            if date_from != None:
                projects = neodb.dbutils.get_id(db.NDB, 'project',
                                           date_start = date_from)
                
            elif date_end != None:
                projects = neodb.dbutils.get_id(db.NDB, 'project',
                                           date_end = date_end)
    
    return projects

def get_from_db(id):
    """
    get_from_db(id)
    
    id: id of project (Mandatory)
    
    Return a Project object from database.
    
    Example:
    import neurodb
    project = neurodb.project.get_from_db(id=17)
    
    """    
    project = Project()
    project.get_from_db(id)
    
    return project


def save_channel_spikes(id_block, channel):
    """
    save_channel_spikes(id_block, channel)
    
    Get spikes from a signal of a channel and save it in database.
    
    
    Parameters
    ----------
    id_block: Integer
              Id of project that channel to process belong.
    channel: Integer
             Number of channel to process.
             
    Returns
    -------
    
    Example
    -------
    
    
    """
    if db.NDB == None:
        db.connect()
    
    ansig = neodb.core.analogsignaldb.get_from_db3(db.NDB, 
                                                   recordingchannel = channel, 
                                                   id_block = id_block)
    
    if len(ansig) != 0:
        ndbdetector = Spike.Detector()
        ndbdetector.set_parameters(sr=int(ansig.sampling_rate))
        spikes, index, thr = ndbdetector.get_spikes(ansig)
        
        for i in range(len(spikes)):
            t_spike = index[i]/float(ansig.sampling_rate)
            segment = neodb.core.analogsignaldb.get_from_db3(db.NDB, 
                                                   recordingchannel = channel, 
                                                   id_block = id_block,
                                                   t_start = t_spike)
            #[(id_seg_ansig, _)] = neodb.get_id(NDB, "analogsignal", )
            spike = neodb.core.SpikeDB(id_segment = segment.id_segment, 
                                       id_recordingchannel = segment.id_recordingchannel,
                                       waveform = spikes[i],
                                       time = t_spike,
                                       index = index[i],
                                       sampling_rate = segment.sampling_rate)
            id_spike = spike.save(db.NDB)
            
    #TODO: returns of the function neurodb.save_channel_spikes

def get_clusters(id_block, channel, method, save=None):
    if method == 'dp':
        user=config.DBUSER
        password=config.DBPASSWORD
        hostname=config.DBHOSTNAME
        dbname=config.DBNAME
        
        sorter = Sorter.DPSorter(dbname, hostname, user, password)
        
    if method == 'paramagnetic':
        if db.NDB == None:
            db.connect()
        
        sorter = Sorter.PMGSorter(db.NDB)
        
    clusters = sorter.get_clusters_fromdb(id_block, channel)
    
    if save == True:
        neodb.core.cluster.save(db.NDB, id_block, channel, clusters)   
    
    return clusters


def draw_clusters(clusters, path = None):
    if db.NDB == None:
        db.connect()
    
    ncluster = len(clusters)
    
    for i in range(ncluster):
        plt.subplot(ncluster,1,i)
        k = 0
        
        for id_spike in clusters[i]:
            spike = neodb.core.spikedb.get_from_db(db.NDB, id_block = 54, channel = 3, id = int(id_spike))
            plt.plot(spike[0].waveform)
            k = k+1
        title = str(i) + ": " + str(k)
        plt.title(title)
    if path:
        plt.savefig(path)
    else:
        plt.show()
    
    


def update_spike_coordenates(id_block, channel):
    #TODO: Create p1, p2 y p3 columns
    from sklearn.preprocessing import normalize
    if db.NDB == None:
        db.connect()
        
    spikes = neodb.core.spikedb.get_from_db(db.NDB, id_block, channel)
    mspikes = []
    
    for spike in spikes:
        mspikes.append(spike.waveform)
    mspikes = np.array(mspikes)
    
    if mspikes == []:
        raise StandardError("Session %s, channel %s have not got spikes.")
    
    pca = PCA(n_components=10)
    #mspikes = normalize(mspikes)
    transf = pca.fit_transform(mspikes)
    
    #transf = Sorter.wave_features(mspikes, 10)
    
    spikes_id = neodb.core.spikedb.get_ids_from_db(db.NDB, id_block, channel)
    
    i = 0
    for p in transf:
        id = spikes_id[i]
        neodb.core.spikedb.update(db.NDB, id = id, p1 = p[0], p2 = p[1], p3 = p[2], p4 = p[3], p5 = p[4], p6 = p[5], p7 = p[6], p8 = p[7], p9 = p[8], p10 = p[9])
        i = i+1
    

# def eliminar(ndb):
#     
#     query = "delete from public.analogsignal where name = '030712_1_00'"
#     cursor.execute(query)
#     
#     query = "delete from public.segment where name = '030712_1_00'"
#     cursor.execute(query)
#         
#     query = "delete from public.block where name = 'session3'"
#     cursor.execute(query)
#         
#     ndb.commit()    

if __name__ == '__main__':
    ndb = db.connect()
    cursor = ndb.cursor()
    
    p = get_from_db(id = 17)
    p.ls_sessions()
    
    #neodb.config_server('192.168.2.2', "oss", "ohm", "demo", "postgres", "postgres")
    #create_project("Project1", "Testing project", "10/10/2014")
    #image = "/home/sergio/iibm/workspace2/NeuroDB/test/feliz.jpg"
    #save = save_session_live(5, 1, '01/01/2014', 'asdfgqh', '/home/sergio/iibm/sandbox')
    #save.start()
    #create_individual("individuo2", "asdfg", "19-02-2013", image)
    
    #print get_individual(8)
    #eliminar(ndb)
    #add_session(14, 6, datetime.date.today(), 'session3', '/home/sergio/sandbox/test', description = "test")
    
    #eliminar(ndb)
    #last_file('/home/sergio/iibm/sandbox')

    #save_channel_spikes(54, 3)
    #update_spike_coordenates(54, 3)
    
    #clusters = get_clusters(54, 3, 'paramagnetic', save=True)
    #clusters = get_clusters('54', '3', 'dp', save=True)
    #draw_clusters(clusters)
    
    pass