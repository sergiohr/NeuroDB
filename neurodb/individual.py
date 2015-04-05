'''
Created on Apr 5, 2015

@author: sergio
'''

import neodb.config
import neodb.dbutils
import matplotlib.pyplot as plt
import os
import db


class Individual(object):
    '''
    Individual contains iformation about a research individual. Like name, days old, etc. 
    '''

    def __init__(self, name = None, description = None, birth_date = None, picture_path= None, index = None):
        '''
        Constructor
        '''
        self.name = name
        self.description = description
        self.birth_date = birth_date
        self.picture_path = picture_path
        self.index = index
        
        if birth_date:
            self.birth_date = neodb.dbutils.get_ppgdate(birth_date)
        else:
            self.birth_date = birth_date
        
    def save(self, connection):
        if self.name == None:
            raise StandardError("Individual must have a name.")
        
        other = neodb.dbutils.get_id(connection, 'individual', name = self.name)
        
        if other != []:
            raise StandardError("There is another individual with name '%s'."%self.name)
        
        cursor = connection.cursor()
        
        if self.picture_path is not None:
            if os.path.isfile(self.picture_path):
                picture_dst = self.__copy_picture(self.picture_path)
            else:
                raise StandardError("'%s' is not a valid path, it does not exist or application can not access."%self.picture_path)
        
        query = """INSERT INTO individual (name, description, birth_date, 
                   picture, index) VALUES (%s, %s, %s, lo_import(%s), %s)"""
        cursor.execute(query,[self.name, self.description, self.birth_date, picture_dst, self.index])
        connection.commit()
        
        [(id, _)] = neodb.dbutils.get_id(connection, 'individual', name = self.name)
        return id
    
    def __copy_picture(self, picture_path, dest = 'host'):
        
        host = neodb.config.read_config('host')
        username = neodb.config.read_config('user')
        pw = neodb.config.read_config('password')
 
        origin = picture_path
        picturename = origin.split('/')[-1]
        dst = '/tmp/' + picturename
 
        ssh = neodb.dbutils.SSHConnection(host, username, pw)
        if dest == 'host':
            ssh.put(origin, dst)
        else:
            ssh.get(origin, dst)
        ssh.close()
        
        return dst
    
    def get_from_db(self, connection, id):
        cursor = connection.cursor()
        query = """ SELECT * FROM individual WHERE id = %s"""
        cursor.execute(query, [id])
        results = cursor.fetchall()
        
        if results != []:
            self.name =          results[0][2]
            self.description =   results[0][3]
            self.birth_date =   results[0][5]
            
            if results[0][5] != None:
                picture_path = '/tmp/%s.jpg'%self.name
                query = """SELECT lo_export( %s, %s )"""
                cursor.execute(query, [results[0][4], picture_path])
                self.picture_path = '/tmp/%s.jpg'%self.name
                self.__copy_picture(self.picture_path, 'local')
        
        results = {}
        results['name'] = self.name
        results['description'] = self.description
        results['birth_date'] = self.birth_date
        results['picture_path'] = self.picture_path
        
        return results
        
def ls_individuals(connection):
    cursor = connection.cursor()
    query = """ SELECT id, name, description FROM individual"""
    cursor.execute(query)
    results = cursor.fetchall()
    
    for i in results:
        print i


def create_individual(name, description, birth_date, picture_path):
    """
    create_individual(name, description, birth_date, picture_path)
    
    Creates a individual in DB.
    
    USE:
    
    create_individual("Bolt", "Raton albino macho", "10/10/2013", "/home/user/pictures/bolt.jpg")
    
    """
    if db.NDB == None:
        db.connect()
    
    individual = Individual(name, description, birth_date, picture_path)
    id = individual.save(db.NDB)
    
    print "Individual created. Id: %s"%id
    return id

def find_individual(name = None, birth_date_from = None, birth_date_end = None):
    if db.NDB == None:
        db.connect()
    
    individuals =[]
    
    if name != None:
        individuals = neodb.dbutils.get_id(db.NDB, 'individual_vw', name = name)
    else:
        if birth_date_from != None and birth_date_end != None:
            individuals = neodb.dbutils.get_id(db.NDB, 'individual_vw',
                                       date_start = birth_date_from,
                                       date_end = birth_date_end)
        else:
            if birth_date_from != None:
                individuals = neodb.dbutils.get_id(db.NDB, 'individual_vw',
                                           date_start = birth_date_from)
                
            elif birth_date_end != None:
                individuals = neodb.dbutils.get_id(db.NDB, 'individual_vw',
                                           date_end = birth_date_end)
    
    return individuals

def get_individual(id):
    if db.NDB == None:
        db.connect()
    
    individual = Individual().get_from_db(db.NDB, id)
    
    return individual

if __name__ == '__main__':
    pass