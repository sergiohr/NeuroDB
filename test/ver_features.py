'''
Created on Mar 4, 2015

@author: sergio
'''

import psycopg2
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


username = 'postgres'
password = 'postgres'
host = '172.16.162.128'
dbname = 'demo'

connection = psycopg2.connect('dbname=%s user=%s password=%s host=%s'%(dbname, username, password, host))
cursor = connection.cursor()
query = """select p3, p4, p5 from SPIKE 
           JOIN segment ON id_segment = segment.id 
           JOIN recordingchannel ON id_recordingchannel = recordingchannel.id 
           WHERE segment.id_block = 76
           AND recordingchannel.index = 1"""

cursor.execute(query)
results = cursor.fetchall()

x = []
y = []
z = []

for i in results:
    x.append(i[0])
    y.append(i[1])
    z.append(i[2])


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z)

# ax.scatter(results[656][0], results[656][1], results[656][2], c='r', marker='^')
# print results[656]

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()