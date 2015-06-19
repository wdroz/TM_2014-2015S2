# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:33:13 2015

@author: droz

DO NOT USE - DEPRECIATED

"""

from DataManager import DataManager
from GoogleFinanceNewsSource import GoogleFinanceNewsSource
from GoogleFinanceMarketSource import GoogleFinanceMarketSource
from ReutersNewsSource import ReutersNewsSource

def easyBuildDataManager(load=False, save=True):
    '''
    method helper for building data manager
    '''
    dm = DataManager()
    if(load):
        dm.load(DataManager.DEFAULT_BACKUP_FILENAME)
    else:
        gfns = GoogleFinanceNewsSource()
        gfms = GoogleFinanceMarketSource()
        rns = ReutersNewsSource('/home/droz/corpus/headlines-docs.csv')
        dm.addNewsSource(gfns)
        dm.addNewsSource(rns)
        dm.setMarketSource(gfms)
        if(save):
            dm.save(DataManager.DEFAULT_BACKUP_FILENAME)
    return dm