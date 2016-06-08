'''
Created on Sep 8, 2014

@author: sergio
'''
import neo.core
import psycopg2
from .. import dbutils
import spikedb
#import dbutils

class RecordingChannelDB(neo.core.RecordingChannel):
    '''
    classdocs
    '''
    def __init__(self, id_block = None, id_recordingchannelgroup = None, index = None,
                        coordinate = None, name = None, description = None,
                        file_origin = None):
        '''
        Constructor
        '''
        self.id = None
        self.id_block = id_block
        self.id_recordingchannelgroup = id_recordingchannelgroup
        self.index = index
        self.coordinate = coordinate
        self.name = name
        self.description = description
        self.file_origin = file_origin
    
    def save(self, connection):
        '''
        Save Recordingchannel into database trough connection. 'connection" is a Psycopg2 connection. You can get
        connection using neodb.connectdb().
        '''
        if self.id_block == None and self.id_recordingchannelgroup == None:
            raise StandardError("RecordingChannel must have a id of Session Block or Recording Channel Group.")
        
        if self.index == None:
            raise StandardError("RecordingChannel must have a index")
        
        self.connection = connection
        cursor = connection.cursor()
        query = """INSERT INTO recordingchannel (id_block, id_recordingchannelgroup,
                                                 index, coordinate, name, 
                                                 description, file_origin)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query,[self.id_block, self.id_recordingchannelgroup, self.index, self.coordinate, self.name, self.description, self.file_origin])
        connection.commit()
        
        if self.id_block and self.id_recordingchannelgroup:
            [(id, _)] = dbutils.get_id(connection, 'recordingchannel',
                                     id_block = self.id_block, 
                                     id_recordingchannelgroup = self.id_recordingchannelgroup, 
                                     index = self.index)
        elif self.id_recordingchannelgroup:
            [(id, _)] = dbutils.get_id(connection, 'recordingchannel', 
                                     id_recordingchannelgroup = self.id_recordingchannelgroup, 
                                     index = self.index)
        elif self.id_block:
            [(id, _)] = dbutils.get_id(connection, 'recordingchannel', 
                                     id_block = self.id_block, 
                                     index = self.index)
        self.id = id
        return id
    
    def get_from_db(self, connection, id):
        self.connection = connection
        cursor = self.connection.cursor()
        query = """ SELECT * FROM recordingchannel WHERE id = %s"""
        cursor.execute(query, [id])
        results = cursor.fetchall()
        
        if results != []:
            self.id =             results[0][0]
            self.index =          results[0][1]
            self.coordinate =     results[0][2]
            self.name =           results[0][3]
            self.description =    results[0][4]
            self.file_origin =    results[0][5]
            self.id_recordingchannelgroup = results[0][7]
            self.id_block =       results[0][6]
        
        results = {}
        results['name'] = self.name
        results['description'] = self.description
        results['file_origin'] = self.file_origin
        return results
    
    def ls_spikes(self):
        idesr = []
        ids = dbutils.get_id(self.connection, "spike", id_recordingchannel=self.id)
        if ids != []:
            for i in ids:
                print "id:%s name:%s"%(i[0], i[1])
                idesr.append(i[0])
        
        return idesr
    
    def get_spikes(self):
        idesr = []
        ids = dbutils.get_id(self.connection, "spike", id_recordingchannel=self.id)
        if ids != []:
            for i in ids:
                idesr.append(i[0])
        
        return idesr
    
    def get_spike(self, id):
        sp = spikedb.get_from_db(self.connection, channel=self.id, id=id)
        if sp != []:
            return sp[0]
        return []
    
    def remove_spikes(self, connection = None):
        if connection == None:
            connection = self.connection
        else:
            self.connection = connection
        
        if connection == None :
            raise StandardError("There are not connection.")
        
        if self.id == None:
            raise StandardError("There are not recordingchannel")
        
        cursor = connection.cursor()
        query = """delete from spike using recordingchannel 
                   where recordingchannel.id = spike.id_recordingchannel and 
                         recordingchannel.id = %s"""
        
        cursor.execute(query, [self.id])
        connection.commit()
        
if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '172.16.162.128'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    rc = RecordingChannelDB()
    rc.get_from_db(dbconn, id=153)
#     rc = RecordingChannelDB(id_block=50, index = 0)
#     id = rc.save(dbconn)
#     print id
#     rc = RecordingChannelDB(index = 0)
#     id = rc.save(dbconn)
    
    