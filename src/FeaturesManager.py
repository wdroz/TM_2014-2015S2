# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:46:45 2015

@author: droz
"""
'''
import os
os.environ['HOME'] = '/tmp'
os.environ['SPARK_WORKER_DIR'] = '/tmp'
'''
#from textblob import TextBlob, Word
import re

class FeaturesV2(object):
    '''
    class for extract features from news
    '''
    def __init__(self, news):
        self.news = news
        #self.publication = re.sub(r'[^A-Za-z.,$! '']', '', news.publication)
        self.publication = re.sub(r'[^A-Za-z$! '']', '', news.publication).upper()
        #self.textBlob = self.textblobLemma(TextBlob(self.publication))
        #self.polarity = self.textBlob.sentiment.polarity
        self.processMarketStatus()
        self.words = self.processWords()
        self.bg2 = self.processBigram(2)
        self.bg3 = self.processBigram(3)
        
    def textblobLemma(self, tb):
        #myTab = []
        #for w in tb.words:
        #    myWord = Word(str(w.lemma))
        #    myWord = Word(str(myWord.lemmatize('v')).upper())
        #    myTab.append(myWord)
        #return TextBlob(' '.join(myTab))
        return tb
        
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
        words = []
        #return [x for x in self.textBlob.words]
        for word in re.split('\W+', self.publication):
            if(word != ''):
                words.append(word)
        return words
        #return self.publication.split(' ')
            
    def processBigram(self, n=2):
        tab = []
        for x in range(len(self.words)-n):
            subTab = []
            for y in range(n):
                subTab.append(self.words[x+y])
            tab.append(" ".join(subTab))
        return tab
        #return [tuple(x) for x in self.textBlob.ngrams(n)]
    
    def processVectorization(self, vectTextBase, vectBGBase):
        myVect = []
        for v in vectTextBase:
            myVect.append(int(v in self.textBlob.words))
            
        for bg in vectBGBase:
            myVect.append(int(bg in self.bg))
            
    def textTransform(self, text):
        return text.upp()
        
    def isGood(self):
        try:
            return self.marketChangeEndToEnd > 0.0
        except:
            return 0
        
    def isGoodN(self, n):
        try:
            return self.marketChange[n] > 0
        except:
            return 0
        
    def giveClasseN(self, n):
        '''
        give the class :
          0 : very bad
          1 : bad
          2 : good
          3 : very good
          
        n is the day of market [0,2]
        '''
        try:
            if (self.marketChange[n] > 0.015):
                return 3
            elif (self.marketChange[n] > 0):
                return 2
            elif (self.marketChange[n] > -0.015):
                return 1
            else:
                return 0
        except:
            return 0

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
        