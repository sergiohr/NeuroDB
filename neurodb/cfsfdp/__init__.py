'''
Created on Jun 27, 2015

@author: sergio
'''

import ctypes
import numpy.ctypeslib as npct
import numpy as np


array_1d_double = npct.ndpointer(dtype=np.double, ndim=1, flags='CONTIGUOUS')
array_1d_int = npct.ndpointer(dtype=np.int64, ndim=1, flags='CONTIGUOUS')
array_2d_double = npct.ndpointer(dtype=np.double, ndim=2, flags='CONTIGUOUS')

libcd = npct.load_library("cfsfdp", "/home/sergio/Proyectos/NeuroDB/NeuroDB/neurodb/cfsfdp")

libcd.get_dc.argtypes = [ctypes.c_char_p, array_1d_double, ctypes.c_int,
                         ctypes.c_float, ctypes.c_int]
libcd.get_dc.restype = ctypes.c_float

libcd.cluster_dp.argtypes = [ctypes.c_char_p, array_1d_double, array_1d_double, 
                             array_1d_double, array_1d_double, array_1d_double, 
                             array_1d_double, ctypes.c_float, ctypes.c_int, 
                             ctypes.c_int, ctypes.c_char_p]
libcd.cluster_dp.restype = ctypes.c_int

libcd.dp.argtypes = [array_1d_double, array_1d_double, ctypes.c_int, 
                     array_1d_double, array_1d_double, ctypes.c_char_p]
libcd.dp.restype = ctypes.c_int



