'''
Created on Apr 21, 2014

@author: sergio
'''

import psycopg2
import neo.core
from .. import dbutils
from quantities import Hz, mV, V, uV
import numpy

class AnalogSignalDB(neo.core.AnalogSignal):
    '''
    classdocs
    '''
    def __init__(self, id_segment = None, id_recordingchannel = None, signal = None, t_start = None,
                       sampling_rate = None, channel_index = None, name = None,
                       description = None, file_origin = None, units = None,
                       index = None):
        '''
        Constructor
        '''
        if signal == None:
            signal = []
        if sampling_rate == None:
            sampling_rate = 14400
        if units == None:
            units = mV
        
        self.signal = signal
        self.sampling_rate=sampling_rate
        self.units=units
        self.t_start = t_start,
        self.channel_index = channel_index
        self.name = name
        self.description = description
        self.file_origin = file_origin
        self.index = index
        
        self.id_segment = id_segment
        self.id_recordingchannel = id_recordingchannel
        
    def save(self, connection):
        # Check mandatory values
        if self.id_segment == None:
            raise StandardError("Analogsignal must have id_segment.")
        
        if self.signal == []:
            raise StandardError("Analogsignal must have a signal.")
        
        if self.name == None:
            raise StandardError("Analogsignal must have a name.")
        
        # Format signal
        signalb = numpy.float16(self.signal)
        
        # QUERY
        cursor = connection.cursor()
        
        query = """INSERT INTO analogsignal 
                   (id_segment, id_recordingchannel, signal, sampling_rate, unit, t_start, channel_index, name, description, file_origin, index)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        unit = str(self.units).split(' ')[1]
        cursor.execute(query,[self.id_segment, self.id_recordingchannel, psycopg2.Binary(signalb),
                              int(self.sampling_rate), unit,
                              int(self.t_start[0]), self.channel_index,
                              self.name, self.description, self.file_origin,
                              self.index])
        
        connection.commit()
        
        # Get ID
        [(id, _)] = dbutils.get_id(connection, 'analogsignal', 
                                 name = self.name, 
                                 channel_index = self.channel_index, 
                                 id_segment = self.id_segment)
        self.id = id
        return id
        
def get_from_db(connection, nchannel, id_block=None , id_segment=None, t_start = None):
    if id_block == None and id_segment == None:
        raise StandardError(""" You must specify id_block or id_segment.""")
    
    # QUERY
    cursor = connection.cursor()
    
    query = """select analogsignal.index,
               analogsignal.signal,
               analogsignal.name
               from analogsignal join segment
               on id_segment = segment.id
               and analogsignal.channel_index = %s"""%nchannel 
    
    query_info = """select analogsignal.index,
                    analogsignal.sampling_rate,
                    analogsignal.unit,
                    analogsignal.description
                    from analogsignal join segment
                    on id_segment = segment.id
                    and analogsignal.channel_index = %s"""%nchannel
    
    if id_block:
        query = query + " and segment.id_block = %s"%id_block
        query_info = query_info + " and segment.id_block = %s"%id_block
        
    if id_segment:
        query = query + " and segment.id = %s"%id_segment
        query_info = query_info + " and segment.id = %s"%id_segment
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # If query get any result return None
    if results == []:
        return []
    
    signal = numpy.array([])
    if len(results)>1:
        for ansig in results:
            signal = numpy.concatenate([signal,numpy.frombuffer(ansig[1], numpy.float16)])
    
    query_info = query_info + " limit 1"
    cursor.execute(query_info)
    results = cursor.fetchall()
    
    units = dbutils.get_quantitie(results[0][2])
    sampling_rate = float(results[0][1])*Hz
    index = int(results[0][1])
    description = results[0][3]
    
    analogsignal = AnalogSignalDB(signal, sampling_rate=sampling_rate, units=units, 
                           index=index, description=description)
    
    print "Loaded succesfuly:"
    print "Lenght: %s"%(len(signal))
    print "Unit: %s"%units
    print "Sampling Rate: %s"%sampling_rate
    
    return analogsignal

def get_from_db2(connection, id_block, **kwargs):
    
    cursor = connection.cursor()
    
    for parameter in kwargs.keys():
        if parameter not in ["id", "id_segment", "id_recordingchannel",
                             "sampling_rate", "t_start", "channel_index",
                             "name", "description", "file_origin", "unit", 
                             "index", "limit"]:
            raise StandardError("""Parameter %s do not belong to analogsignaldb.""")
    
    query = """SELECT analogsignal.id FROM analogsignal join segment
               ON id_segment = segment.id 
               WHERE segment.id_block = %s """%id_block
    constraint = ""
    time_constraint = ""
    
    if kwargs.has_key("t_start"):
        t_start = kwargs.pop('t_start')
        query_time = """SELECT analogsignal.t_start FROM analogsignal join segment
                        on id_segment = segment.id 
                        WHERE segment.id_block = %s and t_start <= %s
                        ORDER BY analogsignal.t_start DESC LIMIT 1"""%(id_block, t_start)
        
        cursor.execute(query_time)
        results = cursor.fetchall()
        t_start = results[0][0]
        
        time_constraint = "and t_start = %s"%t_start  
        
    for key, value in kwargs.iteritems():
        constraint = "%s %s='%s' and "%(constraint,key,value)
    
    if constraint != "" and time_constraint != "":
        query = query + constraint + time_constraint
    elif time_constraint != "":
        query = query + time_constraint
    elif constraint != "":
        constraint = constraint[0:len(constraint)-5]
        query = query + constraint

    cursor.execute(query)
    results = cursor.fetchall()
    
    pass


def get_from_db3(connection, id_block, recordingchannel, **kwargs):
    
    cursor = connection.cursor()
    
    for parameter in kwargs.keys():
        if parameter not in ["id", "id_segment", "id_recordingchannel",
                             "sampling_rate", "t_start", "channel_index",
                             "name", "description", "file_origin", "unit", 
                             "index", "limit"]:
            raise StandardError("""Parameter %s do not belong to analogsignaldb.""")
    
    query = """SELECT analogsignal.index,
                      analogsignal.signal,
                      analogsignal.sampling_rate,
                      analogsignal.unit,
                      analogsignal.name,
                      analogsignal.description,
                      analogsignal.id_recordingchannel,
                      analogsignal.id_segment,
                      analogsignal.channel_index
               FROM analogsignal 
               JOIN segment ON id_segment = segment.id
               JOIN recordingchannel ON id_recordingchannel = recordingchannel.id 
               WHERE segment.id_block = %s and 
               recordingchannel.index = %s"""%(id_block, recordingchannel)
    
    constraint = ""
    time_constraint = ""
    
    if kwargs.has_key("t_start"):
        t_start = kwargs.pop('t_start')
        query_time = """SELECT analogsignal.t_start FROM analogsignal join segment
                        on id_segment = segment.id 
                        WHERE segment.id_block = %s and t_start <= %s
                        ORDER BY analogsignal.t_start DESC LIMIT 1"""%(id_block, t_start)
        
        cursor.execute(query_time)
        results = cursor.fetchall()
        t_start = results[0][0]
        
        time_constraint = " and t_start = %s"%t_start
        
    for key, value in kwargs.iteritems():
        constraint = "%s %s='%s' and "%(constraint,key,value)
    
    if constraint != "" and time_constraint != "":
        query = query + constraint + time_constraint
    elif time_constraint != "":
        query = query + time_constraint
    elif constraint != "":
        constraint = constraint[0:len(constraint)-5]
        query = query + constraint

    cursor.execute(query)
    results = cursor.fetchall()
    
    
    # If query get any result return None
    if results == []:
        return []
    
    signal = numpy.array([])
    if len(results)>=1:
        for ansig in results:
            signal = numpy.concatenate([signal,numpy.frombuffer(ansig[1], numpy.float16)])
    
    info = results[0]
    
    sampling_rate = float(info[2])*Hz
    units = dbutils.get_quantitie(info[3])
    index = int(info[0])
    name = info[4]
    description = info[5]
    
    analogsignal = AnalogSignalDB(signal=signal, sampling_rate=sampling_rate, 
                                  units=units, index=index, description=description)
    
    # If the analog signal is from a only one segment:
    if time_constraint != "":
        analogsignal.id_recordingchannel = info[6]
        analogsignal.id_segment = info[7]
        analogsignal.channel_index = info[8]
    
    return analogsignal

        
if __name__ == '__main__':
    username = 'postgres'
    password = 'postgres'
    host = '192.168.2.2'
    dbname = 'demo'
    url = 'postgresql://%s:%s@%s/%s'%(username, password, host, dbname)
    
    dbconn = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
    #a = AnalogSignalDB(id_segment = 2, signal = [2,2,4,3], units = 'mV', sampling_rate=14400*Hz, t_start = 0)
    #a.save(dbconn)
    
    
#     cursor = dbconn.cursor()
#     cursor.execute('select signal from analogsignal')
#     v = cursor.fetchall()
#     v=v[0]
#     v=v[0]
#     numpy.frombuffer(v, numpy.int16)

    #ansig = AnalogSignalDB([], sampling_rate=14400*Hz, units='mV')
    #ansig = get_from_db3(dbconn, id_block = 54, recordingchannel = 3, t_start = 59)
    ansig = get_from_db3(dbconn, id_block = 54, recordingchannel = 3)
    
    pass