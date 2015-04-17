# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 10:10:20 2015

@author: droz
"""

from DataManager import MarketSource, MarketStatus
import requests
from MessageManager import MessageManager
import datetime
import time

class GoogleFinanceMarketSourceSpark(MarketSource):
    def __init__(self, symboles):
        MarketSource.__init__(self)
        self.url = 'https://www.google.com/finance/historical'
        self.symboles = {}
        print('symboles created')
        for symbole in symboles:
            self.addIfNotExist(symbole)
        
    def requestForMarkets(self, symbole):
        params = {'q' : symbole, 'startdate' : '2000-01-01', 'enddate' : time.strftime('%Y-%m-%d'), 'num' : 30, 'output' : 'csv'}
        r = requests.get(self.url, params=params)
        MessageManager.debugMessage("GoogleFinanceMarketSource : request")
        return r.text.encode('utf-8').split('\n')
        
    def addIfNotExist(self, symbole):
        if(not self.symboles.has_key(symbole)):
            self.symboles[symbole] = self.requestForMarkets(symbole)   
    
    def addMarketStatusToNews(self, news):
        #self.addIfNotExist(new.symbole)
        enddate = news.pubDate + datetime.timedelta(days=7)
        isFirstLline=True
        news.marketStatus = []
        for line in self.symboles[news.symbole]:
            if(isFirstLline):
                isFirstLline=False
            else:
                try:
                    date_m,open_m,high_m,low_m,close_m,volume_m = line.split(',')
                    date_m = datetime.datetime.strptime(date_m, "%d-%b-%y")
                    if(date_m >= news.pubDate and date_m <= enddate):
                        MessageManager.debugMessage("GoogleFinanceMarketSource : adding marketStatus")
                        #for machin in [date_m,open_m,high_m,low_m,close_m,volume_m]:
                        #     MessageManager.debugMessage(str(machin))
                        news.marketStatus.append(MarketStatus(date_m,open_m,high_m,low_m,close_m,volume_m))
                        MessageManager.debugMessage("GoogleFinanceMarketSource : marketStatus added")
                except:
                    pass # empty line
                    MessageManager.debugMessage("GoogleFinanceMarketSource : exception")
        news.marketStatus = sorted(news.marketStatus, key=lambda x:x.market_date)[:3]
        return news
class GoogleFinanceMarketSource(MarketSource):
    '''
    Classe specialisé pour chercher les informations des marchés sur Google Finance
    '''
    def __init__(self):
        MarketSource.__init__(self)
        self.url = 'https://www.google.com/finance/historical'
        self.symboles = {}
        print('symboles created')
        
    def requestForMarkets(self, symbole):
        params = {'q' : symbole, 'startdate' : '2000-01-01', 'enddate' : time.strftime('%Y-%m-%d'), 'num' : 30, 'output' : 'csv'}
        r = requests.get(self.url, params=params)
        MessageManager.debugMessage("GoogleFinanceMarketSource : request")
        return r.text.encode('utf-8').split('\n')
        
    def addIfNotExist(self, symbole):
        if(not self.symboles.has_key(symbole)):
            self.symboles[symbole] = self.requestForMarkets(symbole)   
    
    def addMarketStatusToNews(self, news):
        for new in news:
            self.addIfNotExist(new.symbole)
            enddate = new.pubDate + datetime.timedelta(days=7)
            isFirstLline=True
            new.marketStatus = []
            for line in self.symboles[new.symbole]:
                if(isFirstLline):
                    isFirstLline=False
                else:
                    try:
                        date_m,open_m,high_m,low_m,close_m,volume_m = line.split(',')
                        date_m = datetime.datetime.strptime(date_m, "%d-%b-%y")
                        if(date_m >= new.pubDate and date_m <= enddate):
                            MessageManager.debugMessage("GoogleFinanceMarketSource : add marketStatus")
                            for machin in [date_m,open_m,high_m,low_m,close_m,volume_m]:
                                 MessageManager.debugMessage(str(machin))
                            new.marketStatus.append(MarketStatus(date_m,open_m,high_m,low_m,close_m,volume_m))
                            MessageManager.debugMessage("GoogleFinanceMarketSource : marketStatus added")
                    except:
                        pass # empty line
                        MessageManager.debugMessage("GoogleFinanceMarketSource : exception")
            new.marketStatus = sorted(new.marketStatus, key=lambda x:x.market_date)[:3]