'''
Created on Dec 22, 2013

@author: Sergio Hinojosa Rojas
'''

import numpy as np
from scipy.special import erfc
from scipy import interpolate, signal
import pywt
import glob
import os
import scipy
import shutil


        

class Detector():
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.set_parameters()
        
    def set_parameters(self,
                         w_pre = 20,
                         w_post = 44,
                         detection = 'pos',
                         stdmin = 5.00,
                         stdmax = 50,
                         interpolation = 'y',
                         int_factor = 2,
                         fmin_detect = 300,
                         fmax_detect = 3000,
                         fmin_sort = 300,
                         fmax_sort = 3000,
                         sr = 14400,
                         min_ref_per = 1.5,
                         cluster_linux_dir = '/home/sergio/iibm/workspace2/NeuroDB/src/NeuroDB/signalProcessor'
                       ):
        ''' w_pre           number of pre-event data points stored.
            w_post          number of post-event data points stored.
            detection       type of threshold ('neg','both','pos')
            stdmin          minimum threshold.
            stdmax          maximum threshold.
            fmin_detect     high pass filter for detection.
            fmax_detect     low pass filter for detection.
            fmin_sort       high pass filter for sorting.
            fmax_sort       low pass filter for sorting.
            interpolation   interpolation for alignment.
            int_factor      interpolation factor.
            sr              sampling frequency, in Hz.
            min_ref_per     detector dead time. 
            ref             number of counts corresponding to the dead time'''
        #TODO: algorithm does not works to int_factor != 2
        self.w_pre = w_pre
        self.w_post = w_post
        self.detection = detection
        self.stdmin = stdmin
        self.stdmax = stdmax
        self.fmin_detect = fmin_detect
        self.fmax_detect = fmax_detect
        self.fmin_sort = fmin_sort
        self.fmax_sort = fmax_sort
        self.interpolation = interpolation
        self.int_factor = int_factor
        self.sr = sr
        self.min_ref_per = min_ref_per
        self.ref = np.floor(min_ref_per*sr/1000.0)
        self.cluster_linux_dir = cluster_linux_dir
        
    def __int_spikes(self, spikes):
                    
        ls = self.w_pre + self.w_post
        nspk = len(spikes[:,1])
        
        s = range(len(spikes[1,:]))
        #ints = range(1.0/int_factor,len(spikes[1,:]),1.0/int_factor)
        ints = np.arange(1.0/self.int_factor,len(spikes[1,:])+1.0/self.int_factor,1.0/self.int_factor)
        
        intspikes = np.zeros([1,len(ints)])
        spikes1 = np.zeros([nspk,ls])
        
        try:
            for i in range(nspk):
                if i == 970:
                    pass
                if spikes[i,:].any():
                    print i
                    intspikes = interpolate.spline(s,spikes[i,:],ints)
                    iaux = intspikes[self.w_pre*self.int_factor-1:self.w_pre*self.int_factor+8].argmax(0)
                    iaux = iaux + self.w_pre*self.int_factor-1
                    if iaux-self.w_pre*self.int_factor < 0:
                        iaux = iaux + 1
                    # iaux is index of the max of the spike. To put the max in w_pre, separates
                    # intspikes in 2 vectors
                    v1 = intspikes[iaux-self.w_pre*self.int_factor:iaux+2:self.int_factor]
                    v2 = intspikes[iaux+2:iaux+self.w_post*self.int_factor+1:self.int_factor]
                    spikes1[i,0:self.w_pre] = v1[1:]
                    # padding 
                    for j in range(len(v2)):
                        spikes1[i,j+self.w_pre] = v2[j]
                    
                    #spikes1[i,self.w_pre:ls+1] = v2
                else:
                    spikes1[i,:] = spikes[i,0:ls]
        except:
            print i
        return spikes1

    def __amp_detect(self, x):
        
        ref = np.floor(self.min_ref_per*self.sr/1000.0)
        
        # HIGH-PASS FILTER OF THE DATA
        (b,a) = signal.ellip(2, 0.1, 40, [self.fmin_detect*2.0/self.sr,self.fmax_detect*2.0/self.sr], btype='bandpass', analog=0, output='ba')
        xf_detect = signal.filtfilt(b, a, x)
        (b,a) = signal.ellip(2, 0.1, 40, [self.fmin_sort*2.0/self.sr,self.fmax_sort*2.0/self.sr], btype='bandpass', analog=0, output='ba')
        xf = signal.filtfilt(b, a, x)
        
        
        noise_std_detect = scipy.median(np.abs(xf_detect))/0.6745;
        noise_std_sorted = scipy.median(np.abs(xf))/0.6745;
       
        thr = self.stdmin * noise_std_detect        #thr for detection is based on detected settings.
        thrmax = self.stdmax * noise_std_sorted     #thrmax for artifact removal is based on sorted settings.
        
        # LOCATE SPIKE TIMES
        nspk = 0;
        xaux = np.argwhere(xf_detect[self.w_pre+1:len(xf_detect)-self.w_post-1-1] > thr) + self.w_pre + 1
        xaux = np.resize(xaux,len(xaux))
        xaux0 = 0;
        index = []
        for i in range(len(xaux)):
            if xaux[i] >= (xaux0 + ref):
            # after find a peak it begin search after ref over the last xaux
                iaux = xf[xaux[i]:xaux[i]+np.floor(ref/2.0)].argmax(0)    # introduces alignment
                nspk = nspk + 1
                index.append(iaux + xaux[i])
                xaux0 = index[nspk-1];
        
        # SPIKE STORING (with or without interpolation)
        ls = self.w_pre + self.w_post
        spikes = np.zeros([nspk,ls+4])
        xf = np.concatenate((xf,np.zeros(self.w_post)),axis=0)
        
        for i in range(nspk):                          # Eliminates artifacts
            if np.max( np.abs( xf[index[i]-self.w_pre:index[i]+self.w_post] )) < thrmax :
                spikes[i,:] = xf[index[i]-self.w_pre-1:index[i]+self.w_post+3]
     
        aux = np.argwhere(spikes[:,self.w_pre] == 0)       #erases indexes that were artifacts
        if len(aux) != 0:
            aux = aux.reshape((1,len(aux)))[0]
            spikes = np.delete(spikes, aux, axis = 0)
            index = np.delete(index,aux)
 
        if self.interpolation == 'y':
            # Does interpolation
            spikes = self.__int_spikes(spikes)

        return spikes, thr, index
        
    def get_spikes(self, analogSignal):
        spikes, thr, index = self.__amp_detect(analogSignal)
        
        return spikes, index, thr

if __name__ == '__main__':
    pass