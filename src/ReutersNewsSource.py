# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 10:13:13 2015

@author: droz
"""

from DataManager import NewsSource, News
from MessageManager import MessageManager
import datetime
import time

class ReutersNewsSourceHDFS(NewsSource):
    '''
    Classe qui est charger de récolter les news depuis l'HDFS
    '''
    def __init__(self, filenameRdd):
        NewsSource.__init__(self)
        self.filenameRdd = filenameRdd
    
    def lookingAll(self, symbole, keywords):
        startDate = "2000-01-01"
        endDate = time.strftime('%Y-%m-%d')
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        return self.lookingAt(symbole, startDate, endDate, keywords)
    
    def lookingAt(self, symbole, startDate, endDate, keywords):
        upperKeywords = [x.upper() for x in keywords]
        MessageManager.debugMessage("ReutersNewsSourceHDFS : start reading Reuters corpus")
        def hasAnyofTheresKeywords(keywords, text):
            for word in keywords:
                if(word in text):
                    return True
            return False
        
        def fct(line):
            try:
                lines = line.split(',')
                date = datetime.datetime.strptime(lines[0], "%Y-%m-%d %H:%M:%S")
                if(date >= startDate and date <= endDate):
                    head = lines[1]
                    msg = ''.join(lines[2:])
                    if(hasAnyofTheresKeywords(upperKeywords, head.upper()) or hasAnyofTheresKeywords(upperKeywords, msg.upper())):
                        #MessageManager.debugMessage("ReutersNewsSource : head or msg has keywords")
                        return News(pubDate=date, symbole=symbole, publication=head, pubSource="Reuters")
            except:
                pass # explicative line or empty
            return None
            
        newsRdd = self.filenameRdd.map(fct).filter(lambda x: x != None)
        MessageManager.debugMessage("ReutersNewsSourceHDFS : stop reading Reuters corpus")
        return newsRdd

class ReutersNewsSource(NewsSource):
    '''
    Classe qui est charger de récolter les news depuis un chemin local
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
                    if(self.hasAnyofTheresKeywords(upperKeywords, head.upper()) or self.hasAnyofTheresKeywords(upperKeywords, msg.upper())):
                        MessageManager.debugMessage("ReutersNewsSource : head or msg has keywords")
                        self.news.append(News(pubDate=date, symbole=symbole, publication=head, pubSource="Reuters"))
            except:
                pass # explicative line or empty
        f.close()
        MessageManager.debugMessage("ReutersNewsSource : stop reading Reuters corpus")
        MessageManager.debugMessage("ReutersNewsSource : %d news found" % len(self.news))