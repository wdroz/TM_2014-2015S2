# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:46:45 2015

@author: droz
"""

from textblob import TextBlob
import re

class Features(object):
    def __init__(self, news):
        self.news = news
        self.publication = re.sub(r'[^A-Za-z1234567890.,$! '']', '', news.publication)    
        #TODO remove special chars
        self.textBlob = TextBlob(self.publication)
        self.polarity = self.textBlob.sentiment.polarity
        self.processMarketStatus()
    
    def processMarketStatus(self):
        self.marketChange = []
        self.marketChangeEndToEnd = 0
        for marketStatus in self.news.marketStatus:
            deltaMarket = marketStatus.market_close-marketStatus.market_open
            self.marketChange.append(float(deltaMarket)/marketStatus.market_open)     
            
        try:
            deltaMarket = self.news.marketStatus[-1].market_close-self.news.marketStatus[0].market_open
            self.marketChangeEndToEnd = float(deltaMarket)/self.news.marketStatus[0].market_open
        except:
            pass # empty
            
    def isDoubleChecked(self):
        return (self.isGood() and (self.polarity > 0)) or ((not self.isGood()) and (self.polarity <= 0))         
        
    def isDoubleCheckedN(self, n):
        return ((self.marketChange[n] > 0) and (self.polarity > 0)) or ((self.marketChange[n] <= 0) and (self.polarity <= 0))  
            
    def isGood(self):
        return self.marketChangeEndToEnd > 0.0
        
    def __str__(self):
        return str(self.getVector()) + '\t -> ' + ('good' if self.isGood() else 'bad')
        
    def getVector(self):
        return [self.polarity, self.marketChangeEndToEnd] + self.marketChange
        
    def getPairforClassification(self):
        return (self.publication, "pos" if self.isGood() else 'neg')

class FeaturesManager(object):
    def __init__(self):
        pass
        