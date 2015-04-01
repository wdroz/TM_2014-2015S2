# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:46:45 2015

@author: droz
"""

from textblob import TextBlob, Word
import re

class FeaturesV2(object):
    def __init__(self, news):
        self.news = news
        self.publication = re.sub(r'[^A-Za-z.,$! '']', '', news.publication)    
        self.textBlob = self.textblobLemma(TextBlob(self.publication))
        self.polarity = self.textBlob.sentiment.polarity
        self.processMarketStatus()
        self.bg2 = self.processBigram(2)
        self.bg3 = self.processBigram(3)
        self.words = self.processWords()
        
    def textblobLemma(self, tb):
        myTab = []
        for w in tb.words:
            myWord = Word(str(w.lemma))
            myWord = Word(str(myWord.lemmatize('v')).upper())
            myTab.append(myWord)
        return TextBlob(' '.join(myTab))
        
    def __hash__(self):
        return self.news.__hash__()
    
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
            
    def processWords(self):
        return [x for x in self.textBlob.words]
            
    def processBigram(self, n=2):
        return [tuple(x) for x in self.textBlob.ngrams(n)]
    
    def processVectorization(self, vectTextBase, vectBGBase):
        myVect = []
        for v in vectTextBase:
            myVect.append(int(v in self.textBlob.words))
            
        for bg in vectBGBase:
            myVect.append(int(bg in self.bg))
            
    def textTransform(self, text):
        return text.upp()
        
    def isGood(self):
        return self.marketChangeEndToEnd > 0.0

class Features(object):
    def __init__(self, news):
        self.news = news
        self.publication = re.sub(r'[^A-Za-z.,$! '']', '', news.publication)    
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
        
    def isGoodN(self, n):
        return self.marketChange[n] > 0
        
    def __str__(self):
        return str(self.getVector()) + '\t -> ' + ('good' if self.isGood() else 'bad')
        
    def getVector(self):
        return [self.polarity, self.marketChangeEndToEnd] + self.marketChange
        
    def getPairforClassification(self):
        return (self.publication, "pos" if self.isGood() else 'neg')
        
    def getPairforClassificationTextBlob(self):
        return (self.textBlob, "pos" if self.isGood() else 'neg')

class FeaturesManager(object):
    def __init__(self):
        pass
        