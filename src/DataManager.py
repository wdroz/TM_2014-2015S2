# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:54:03 2015

@author: droz
"""

import datetime
import time
import pickle
import json

class NewsPrediction(object):
    def __init__(self, news=None, prediction=0):
        try:
            self.prediction = prediction
            self.publication = news.publication
            self.pubDate = str(news.pubDate)
            self.pubSource = news.pubSource 
            self.symbole = news.symbole
        except:
            pass # news is None
        
    def json(self):
        return json.dumps(self.__dict__)
        
    def __str__(self):
        myString = '---\n'
        myString += '%s\t%s\t%s\tfrom %s\n' % (self.symbole, self.pubDate, self.publication, self.pubSource)
        myString += '\tpredValue is %s\n' % self.prediction
        myString += '---'
        return myString

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
                 marketStatus=[], resetTime=True):
        self.pubDate = pubDate
        if(resetTime):
            try:
                self.pubDate = pubDate.replace(hour=0, minute=0, second=0)
            except:
                pass # if None
        self.symbole = symbole
        self.publication = publication
        self.pubSource = pubSource
        self.marketStatus = marketStatus
        
    def __str__(self):
        myString = '[%s] from %s : %s\n' % (str(self.pubDate.strftime('%d-%m-%Y')), str(self.pubSource)[:30], str(self.publication))
        for marketStatus in self.marketStatus:
            myString += '\t' + str(marketStatus) + '\n'
        return myString
        
    def __hash__(self):
        return str(self.publication).__hash__()
        
    def __eq__(self, other):
        return other.__hash__ == self.__hash__

class DataManager(object):
    '''
    Pas encore utilisé
    '''
    DEFAULT_BACKUP_FILENAME='dataManager.p'
    
    def __init__(self):
        self.listNewsSource = []
        self.marketSource = None
        self.news = []
        
    def saveNewsWithDataWritter(self, dataWritter):
        dataWritter.serialize(self.news)
        
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
            newsSource.clean()
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
        
    def clean(self):
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