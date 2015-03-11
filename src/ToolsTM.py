# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:33:13 2015

@author: droz
"""

from DataManager import DataManager, GoogleFinanceMarketSource, ReutersNewsSource
from GoogleFinanceNewsSource import GoogleFinanceNewsSource

def easyBuildDataManager(load=False, save=True):
    dm = DataManager()
    if(load):
        dm.load(DataManager.DEFAULT_BACKUP_FILENAME)
    else:
        gfns = GoogleFinanceNewsSource()
        gfms = GoogleFinanceMarketSource()
        rns = ReutersNewsSource('/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv')
        dm.addNewsSource(gfns)
        dm.addNewsSource(rns)
        dm.setMarketSource(gfms)
        if(save):
            dm.save(DataManager.DEFAULT_BACKUP_FILENAME)
    return dm