# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:54:03 2015

@author: droz
"""

import requests
import re
import datetime
import HTMLParser

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
        self.market_volume = int(market_volume)
        
    def __str__(self):
        return 'Date %s,Open %f,High %f,Low %f,Close %f,Volume %d' % (self.market_date.strftime('%d-%m-%Y'), 
                                                                      self.market_open, 
                                                                      self.market_high,
                                                                      self.market_low,
                                                                      self.market_close,
                                                                      self.market_volume)

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
        myString = '[%s] from %s : %s\n' % (str(self.pubDate.strftime('%d-%m-%Y')), str(self.pubSource)[:30], str(self.publication)[:50])
        for marketStatus in self.marketStatus:
            myString += '\t' + str(marketStatus) + '\n'
        return myString

class DataManager(object):
    '''
    Pas encore utilié
    '''
    pass

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

class GoogleFinanceNewsSource(NewsSource):
    '''
    Classe specialisé pour chercher les informations sur Google Finance
    '''
    def __init__(self):
        NewsSource.__init__(self)
        self.url = 'https://www.google.com/finance/company_news'
        self.expNews = '<div style="width:100%;">([^/]+)</div>'
        self.expDate = '<span class=date>([^/]+)</span>'
        self.expPubSource = '<span class=src>([^/]+)</span>'
        self.num = 10
        self.h = HTMLParser.HTMLParser()
        
    def lookingAt(self, symbole, startDate, endDate):
        hasMoreQuote=True
        params = {'q' : symbole, 'startdate' : str(startDate), 'enddate' : str(endDate), 'start' : 0, 'num' : self.num}
        while(hasMoreQuote):
            r = requests.get(self.url, params=params)
            print('request...')
            text = self.h.unescape(r.text).encode('utf-8')
            quotes = re.findall(self.expNews, text)  
            dates = re.findall(self.expDate, text)
            sources = re.findall(self.expPubSource, text)
            if(len(quotes) < self.num):
                hasMoreQuote=False
            for cpt in xrange(len(quotes)):
                try:
                    #Feb 26, 2015
                    date = datetime.datetime.strptime(dates[cpt], "%b %d, %Y")
                    self.news.append(News(pubDate=date, symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
                except:
                    print('some news has been lost...')
            params['start'] += self.num
            

class GoogleFinanceMarketSource(MarketSource):
    '''
    Classe specialisé pour chercher les informations des marchés sur Google Finance
    '''
    def __init__(self):
        MarketSource.__init__(self)
        self.url = 'https://www.google.com/finance/historical'
    
    def addMarketStatusToNews(self, news):
        for new in news:
            enddate = new.pubDate + datetime.timedelta(days=7)
            params = {'q' : new.symbole, 'startdate' : new.pubDate.strftime('%Y-%m-%d'), 'enddate' : enddate.strftime('%Y-%m-%d'), 'num' : 30, 'output' : 'csv'}
            r = requests.get(self.url, params=params)
            isFirstLline=True
            new.marketStatus = []
            for line in r.text.encode('utf-8').split('\n'):
                if(isFirstLline):
                    isFirstLline=False
                else:
                    try:
                        date_m,open_m,high_m,low_m,close_m,volume_m = line.split(',')
                        date_m = datetime.datetime.strptime(date_m, "%d-%b-%y")
                        new.marketStatus.append(MarketStatus(date_m,open_m,high_m,low_m,close_m,volume_m))
                    except:
                        pass # empty line
            new.marketStatus = sorted(new.marketStatus, key=lambda x:x.market_date)[:3]
    
class ReutersNewsSource(NewsSource):
    '''
    pas encore utilisé
    '''
    pass