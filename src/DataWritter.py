# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:02:21 2015

@author: droz
"""

import time
import os

class DataWritter(object):
    '''
    class for serialize data with custom serializing methods
    '''
    def __init__(self, path, serializer):
        self.serializer = serializer
        self.path = path
        self.cpt = 0
        
    def serializeOne(self, item):
        '''
        serialize an item with the serializer giver in the __init__.
        Then, the data will be written on the path (local)
        '''
        fullpath = os.path.join(self.path, '%s-%d.p' % (time.strftime('%Y-%m-%d_%H_%M_%S'), self.cpt))
        with open(fullpath, 'w') as outfile:
            self.serializer(item.__dict__, outfile)
        self.cpt += 1
        
    
    def serialize(self, collection):
        '''
        Serialize a collection of item by calling serializeOne several time
        '''
        for item in collection:
            self.serializeOne(item)
        
    