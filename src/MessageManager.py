# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:42:06 2015

@author: droz
"""

class MessageManager(object):
    '''
    class for manager messages.
    import loggin will be better...
    '''
    DEBUG = True
    
    @staticmethod
    def debugMessage(text):
        '''
        method for print message into console (only if DEBUG are True)
        '''
        if(MessageManager.DEBUG):
            print(text)