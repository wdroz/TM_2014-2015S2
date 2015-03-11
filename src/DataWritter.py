# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:02:21 2015

@author: droz
"""

import time
import os

class DataWritter(object):
    def __init__(self, path, serializer):
        self.serializer = serializer
        self.path = path
        self.cpt = 0
        
    def serializeOne(self, item):
        fullpath = os.path.join(self.path, '%s-%d.p' % (time.strftime('%Y-%m-%d_%H_%M_%S'), self.cpt))
        with open(fullpath, 'w') as outfile:
            self.serializer(item.__dict__, outfile)
        self.cpt += 1
        
    
    def serialize(self, collection):
        for item in collection:
            self.serializeOne(item)
        
    