'''
Created on Jan 8, 2014

@author: sergio
'''

import os
import NeuroDB.config as config

def get_trials():
    return os.listdir(config.TRIALS_PATH)
    pass


if __name__ == '__main__':
    pass