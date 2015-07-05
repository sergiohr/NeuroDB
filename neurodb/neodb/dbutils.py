'''
Created on Apr 20, 2014

@author: sergio
'''
import re
import datetime
import psycopg2
import paramiko
import quantities

class SSHConnection(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, host, username, password, port=22):
        """Initialize and setup connection"""
        self.sftp = None
        self.sftp_open = False
 
        # open SSH Transport stream
        self.transport = paramiko.Transport((host, port))
 
        self.transport.connect(username=username, password=password)
 
    #----------------------------------------------------------------------
    def _openSFTPConnection(self):
        """
        Opens an SFTP connection if not already open
        """
        if not self.sftp_open:
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            self.sftp_open = True
 
    #----------------------------------------------------------------------
    def get(self, remote_path, local_path=None):
        """
        Copies a file from the remote host to the local host.
        """
        self._openSFTPConnection()        
        self.sftp.get(remote_path, local_path)        
 
    #----------------------------------------------------------------------
    def put(self, local_path, remote_path=None):
        """
        Copies a file from the local host to the remote host
        """
        self._openSFTPConnection()
        self.sftp.put(local_path, remote_path)
 
    #----------------------------------------------------------------------
    def close(self):
        """
        Close SFTP connection and ssh connection
        """
        if self.sftp_open:
            self.sftp.close()
            self.sftp_open = False
        self.transport.close()

def get_ppgdate(date):
    """
    'date' may be a datetime.date type or string with format 'dd-mm-yyyy' or 
    'dd/mm/yyyy'. Function returns psycopg2.Date
    """
    if type(date) == datetime.date:
        return psycopg2.Date(date.year, date.month, date.day)
    
    if type(date) != str:
        raise StandardError("Invalid date type. It must be 'datetime.date' or " + 
                             "string with format 'dd-mm-yyyy' or 'dd/mm/yyyy'")
    
    match = re.match('(^(\d{1,2})[\/|-](\d{1,2})[\/|-](\d{4})$)', date)
    if match:
        dd = int(match.groups()[1])
        mm = int(match.groups()[2])
        yyyy = int(match.groups()[3])
        if not((1<dd<31) or (1<mm<12)):
            raise StandardError("Invalid month or day value. Format: 'dd-mm-yyyy' or 'dd/mm/yyyy'")
        
        return psycopg2.Date(yyyy,mm,dd)
    else:
        raise StandardError("Invalid date format. It must be 'dd-mm-yyyy' or 'dd/mm/yyyy'")


def get_datetimedate(date):
    """
    'date' must be a string with format 'dd-mm-yyyy' or 
    'dd/mm/yyyy'. Function returns datetime.date
    """
    if type(date) != str:
        raise StandardError("Invalid date type. It must be 'datetime.date' or " + 
                             "string with format 'dd-mm-yyyy' or 'dd/mm/yyyy'")
    
    match = re.match('(^(\d{1,2})[\/|-](\d{1,2})[\/|-](\d{4})$)', date)
    if match:
        dd = int(match.groups()[1])
        mm = int(match.groups()[2])
        yyyy = int(match.groups()[3])
        if not((1<=dd<=31) or (1<=mm<=12)):
            raise StandardError("Invalid month or day value. Format: 'dd-mm-yyyy' or 'dd/mm/yyyy'")
        
        return datetime.date(yyyy,mm,dd)
    else:
        raise StandardError("Invalid date format. It must be 'dd-mm-yyyy' or 'dd/mm/yyyy'")

def get_quantitie(unit):
    if unit not in ['V', 'v', 'mV', 'mv', 'uV', 'uv']:
        raise StandardError("Parameter must be 'V' , 'mV' or 'uV'")
    
    if unit == 'V' or unit == 'v':
        return quantities.V
    if unit == 'mV' or unit == 'mv':
        return quantities.mV
    if unit == 'uV' or unit == 'uv':
        return quantities.uV

def get_id(connection, table_name, **kwargs):
    """
    Use:
    connection = neodb.dbconnect(name, username, password, host)
    
    # Returns id of project with name "projectname" 
    [(id, _)] = get_id(connection, "project", name = "projectname")
    
    # Returns all segments'id between '2014-03-01' and '2014-03-21':
    ids = get_id(connection, "segment", date_start = '2014-03-01', date_end = '2014-03-21')
    
    You can add all parameters as columns the table have.
    Function returns the follow format:
        [(id1, name1), (id2, name2), ...]
    """
    cursor = connection.cursor()
    columns = column_names(table_name, connection)
    
    ids = []
    
    if kwargs == {}:
        query = "SELECT id, name FROM " + table_name
        cursor.execute(query)
        results = cursor.fetchall()
        
        for i in results:
            ids.append((i[0],str(i[1])))
            
    else:
        query = "SELECT id, name FROM " + table_name + " WHERE "
        constraint = ""
        time_constraint = ""
        
        if kwargs.has_key("date_start") and kwargs.has_key("date_end"):
            time_constraint = "date >= '%s' and date <= '%s'"%(kwargs.pop('date_start'),kwargs.pop('date_end'))
        elif kwargs.has_key("date_start"):
            time_constraint = "date >= '%s'"%kwargs.pop('date_start')
        elif kwargs.has_key("date_end"):
            time_constraint = "date <= '%s'"%kwargs.pop('date_end')
            
        for key, value in kwargs.iteritems():
            if key in columns:
                constraint = "%s %s='%s' and "%(constraint,key,value)
            else:
                raise ValueError('%s is not member of %s'%(key,object))
        
        if constraint != "" and time_constraint != "":
            query = query + constraint + time_constraint
        elif time_constraint != "":
            query = query + time_constraint
        elif constraint != "":
            constraint = constraint[0:len(constraint)-5]
            query = query + constraint
    
        cursor.execute(query)
        results = cursor.fetchall()
        
        for i in results:
            ids.append((i[0],str(i[1])))
        
    return ids
    
def column_names(table_name, connection):
    cursor = connection.cursor()        
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = '%s'"%table_name)
    results = cursor.fetchall()
    
    columns = []
    for i in results:
        columns.append(str(i[0]))
    
    return columns

if __name__ == '__main__':
    print get_ppgdate(3)