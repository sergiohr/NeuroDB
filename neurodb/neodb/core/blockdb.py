'''
Created on Apr 20, 2014

@author: sergio
'''

import psycopg2

import neo.core
from .. import dbutils
import recordingchanneldb

class BlockDB(neo.core.Block):
    '''
    classdocs
    '''
    def __init__(self, id_project = None, id_individual = None, name = None,
                       description = None, file_origin = None,
                       file_datetime = None, rec_datetime = None, index = None):
        '''
        Constructor
        '''
        
        neo.core.Block.__init__(self, name, description, file_origin,
                                      file_datetime, rec_datetime, index)
        self.id_project = id_project
        self.id_individual = id_individual
        self.id = None
        self.connection = None
    
    def save(self, connection):
        # Check mandatory values
        if self.id_project == None or self.id_individual == None:
            raise StandardError("Block Session must have id_project and id_individual.")
            
        if self.name == None:
            raise StandardError("Block Session must have a name.")
        
        other = dbutils.get_id(connection, 'block', name = self.name)
        if other != []:
            raise StandardError("There is another block session with name '%s'."%self.name)
        
        file_datetime = None
        rec_datetime = None
        if self.file_datetime:
            file_datetime = dbutils.get_ppgdate(self.file_datetime)
        if self.rec_datetime:
            rec_datetime = dbutils.get_ppgdate(self.rec_datetime)
        
        # QUERY
        cursor = connection.cursor()
        
        query = """INSERT INTO block 
                   (id_project, id_individual, name, description, file_datetime,
                   rec_datetime, file_origin, index)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(query,[self.id_project, self.id_individual,
                              self.name, self.description, file_datetime,
                              rec_datetime, self.file_origin, self.index])
        connection.commit()
        
        # Get ID
        [(id, _)] = dbutils.get_id(connection, 'block', name = self.name)
        self.id = id
        return id
    
    def get_from_db(self, connection, id):
        self.connection = connection
        
        cursor = self.connection.cursor()
        query = """ SELECT * FROM block WHERE id = %s"""
        cursor.execute(query, [id])
        results = cursor.fetchall()
        
        
        if results != []:
            self.id =            results[0][0]
            self.name =          results[0][6]
            self.description =   results[0][7]
            self.file_origin =   results[0][8]
            self.file_datetime = results[0][3]
            self.rec_datetime =  results[0][4]
        
        results = {}
        results['name'] = self.name
        results['description'] = self.description
        results['file_origin'] = self.file_origin
        results['file_datetime'] = self.file_datetime
        results['rec_datetime'] = self.rec_datetime
        
        results['segments'] = self.__get_segments_id(id, self.connection)
        
        return results
    
    def ls_channels(self):
        idesr = []
        if self.id != None:
            ids = dbutils.get_id(self.connection, 'recordingchannel', id_block=self.id)
            if ids != []:
                for i in ids:
                    print ("id: %s, name: %s")%(i[0],i[1])
                    idesr.append(i[0])
            
        return idesr
    
    def get_channels(self):
        idesr = []
        if self.id != None:
            ids = dbutils.get_id(self.connection, 'recordingchannel', id_block=self.id)
            if ids != []:
                for i in ids:
                    idesr.append(i[0])
        
        lschannel = []
        for id in idesr:
            ch = recordingchanneldb.RecordingChannelDB()
            ch.get_from_db(self.connection, id)
            lschannel.append({'id':id, 'channel':ch.index})
            
        return lschannel
    
    def get_channel(self, id):
        rc = recordingchanneldb.RecordingChannelDB()
        rc.get_from_db(self.connection, id)
        
        return rc
        
    
    def __get_segments_id(self, id, connection):
        cursor = connection.cursor()
        query = """ SELECT id FROM segment WHERE id_block = %s"""
        cursor.execute(query, [id])
        results = cursor.fetchall()
        
        ids = []
        
        for id in results:
            ids.append(id[0])
            
        return ids
        

if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    #b = BlockDB(id_project = 5, id_individual = 1, name = 'bloque prueba', rec_datetime="19-05-2014")
    b = BlockDB()
    b.get_from_db(dbconn,2)
    print b.save(dbconn)