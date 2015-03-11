# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:54:03 2015

@author: droz
"""

import requests
import re
import datetime
import time
import pickle

from MessageManager import MessageManager

class MarketStatus(object):
    '''
    Classe qui contient les informations principales boursière d'un jour.
    '''
    def __init__(self, market_date=None, market_open=0, market_high=0, 
                 market_low=0, market_close=0, market_volume=0):
        self.market_date = market_date
        self.market_open = float(market_open)
        self.market_high = float(market_high)
        self.market_low = float(market_low)
        self.market_close = float(market_close)
        try:
            self.market_volume = int(market_volume)
        except:
            self.market_volume = None # this information isn't alway availlable
        
    def __str__(self):
        return 'Date %s,Open %f,High %f,Low %f,Close %f,Volume %d' % (self.market_date.strftime('%d-%m-%Y'), 
                                                                      self.market_open, 
                                                                      self.market_high,
                                                                      self.market_low,
                                                                      self.market_close,
                                                                      self.market_volume if self.market_volume != None else 0)

class News(object):
    '''
    Classe qui permet de stocker des news
    '''
    def __init__(self, pubDate=None, symbole='', publication='', pubSource='', 
                 marketStatus=[]):
        self.pubDate = pubDate
        self.symbole = symbole
        self.publication = publication
        self.pubSource = pubSource
        self.marketStatus = marketStatus
        
    def __str__(self):
        myString = '[%s] from %s : %s\n' % (str(self.pubDate.strftime('%d-%m-%Y')), str(self.pubSource)[:30], str(self.publication))
        for marketStatus in self.marketStatus:
            myString += '\t' + str(marketStatus) + '\n'
        return myString

class DataManager(object):
    '''
    Pas encore utilisé
    '''
    DEFAULT_BACKUP_FILENAME='dataManager.p'
    
    def __init__(self):
        self.listNewsSource = []
        self.marketSource = None
        self.news = []
        
    def addNewsSource(self, newsSource):
        self.listNewsSource.append(newsSource)

    def setMarketSource(self, marketSource):
        self.marketSource = marketSource        
        
    def save(self, filename):
        pickle.dump(self.__dict__, open(filename, "wb" ))
        
    def load(self, filename):
        self.__dict__ = pickle.load(open(filename, "rb" ))
        
    def lookingAll(self, symbole, keywords):
        startDate = "2000-01-01"
        endDate = time.strftime('%Y-%m-%d')
        self.lookingAt(symbole, startDate, endDate, keywords)
        
    def lookingAt(self, symbole, startDate, endDate, keywords):
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        for newsSource in self.listNewsSource:
            newsSource.lookingAt(symbole, startDate, endDate, keywords)
            self.marketSource.addMarketStatusToNews(newsSource.news)
            self.news += newsSource.news
        self.news = sorted(self.news, key=lambda x:x.pubDate)
        
    def __str__(self):
        myString = ''
        for new in self.news:
            myString += str(new) + '\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n'
        myString += '\n%d News from %d sources' % (len(self.news), len(self.listNewsSource))
        return myString
    

class NewsSource(object):
    '''
    Classe abstraite qui définit le contrat pour un fournisseur de news
    '''
    def __init__(self):
        self.news = []
    
    def lookingAt(self, symbole, startDate, endDate):
        '''
        Chercher des news pour symbole depuis startDate à endDate
        '''
        pass
    
    def lookingAll(self, symbole):
        '''
        Chercher toutes les news disponibles pour symbole
        '''
        pass
    
    def __str__(self):
        myString = ''
        for new in self.news:
            myString += str(new) + '\n++++++++++++++++++++++++++++++++++++\n'
        return myString
        
    def save(self, filename):
        pickle.dump(self.__dict__, open(filename, "wb" ))
        
    def load(self, filename):
        self.__dict__ = pickle.load(open(filename, "rb" ))

class MarketSource(object):
    '''
    Classe abstraite pour les sources du marchés
    '''
    def __init__(self):
        pass
    
    def addMarketStatusToNews(self, news):
        '''
        Ajoute aux news les MarketStatus pour les 3 prochain jours
        '''
        pass            

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
    
class ReutersNewsSource(NewsSource):
    '''
    pas encore utilisé
    '''
    def __init__(self, filename):
        NewsSource.__init__(self)
        self.filename = filename
        
    def hasAnyofTheresKeywords(self, keywords, text):
        for word in keywords:
            if(word in text):
                return True
        return False
        
    def lookingAt(self, symbole, startDate, endDate, keywords):
        upperKeywords = [x.upper() for x in keywords]
        MessageManager.debugMessage("ReutersNewsSource : start reading Reuters corpus")
        f = open(self.filename, 'r')
        for line in f:
            try:
                lines = line.split(',')
                date = datetime.datetime.strptime(lines[0], "%Y-%m-%d %H:%M:%S")
                if(date >= startDate and date <= endDate):
                    head = lines[1]
                    msg = ''.join(lines[2:])
                    if(self.hasAnyofTheresKeywords(upperKeywords, head) or self.hasAnyofTheresKeywords(upperKeywords, msg)):
                        MessageManager.debugMessage("ReutersNewsSource : head or msg has keywords")
                        self.news.append(News(pubDate=date, symbole=symbole, publication=head, pubSource="Reuters"))
            except:
                pass # explicative line or empty
        f.close()
        MessageManager.debugMessage("ReutersNewsSource : stop reading Reuters corpus")
        MessageManager.debugMessage("ReutersNewsSource : %d news found" % len(self.news))