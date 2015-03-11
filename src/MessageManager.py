# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:42:06 2015

@author: droz
"""

class MessageManager(object):
    DEBUG = True
    
    @staticmethod
    def debugMessage(text):
        if(MessageManager.DEBUG):
            print(text)