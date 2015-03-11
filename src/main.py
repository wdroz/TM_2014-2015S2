# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:55:38 2015

@author: droz
"""
import DataManager
from ToolsTM import easyBuildDataManager

if __name__ == "__main__":
    '''
    gfns = GoogleFinanceNewsSource()
    gfns.lookingAt('NASDAQ:GOOG','2000-01-01','2015-03-03')
    
    gfms = GoogleFinanceMarketSource()
    gfms.addMarketStatusToNews(gfns.news)
    print(str(gfns))
    '''
    
    #rns = ReutersNewsSource('/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv')
    #rns.lookingAt("Googl", '2000-01-01','2015-03-03')

    #gfms = GoogleFinanceMarketSource()
    #gfms.addMarketStatusToNews(rns.news)
    
    #rns.save('backup.p')
    
    #rns.load('backup.p')    
    
    #print(str(rns))
    DataManager.MessageManager.DEBUG = True
    dm = easyBuildDataManager(load=False, save=True)
    #dm.lookingAll('NASDAQ:GOOGL', ['GOOG'])
    #dm.lookingAll('SCMN.VX', ['SWISSCOM'])
    #dm.save('googleAndSwisscom.p')
    dm.load('googleAndSwisscom.p')    
    print(str(dm))
    