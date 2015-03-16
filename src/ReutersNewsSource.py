# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 10:13:13 2015

@author: droz
"""

from DataManager import NewsSource, News
from MessageManager import MessageManager
import datetime

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
                    if(self.hasAnyofTheresKeywords(upperKeywords, head.upper()) or self.hasAnyofTheresKeywords(upperKeywords, msg.upper())):
                        MessageManager.debugMessage("ReutersNewsSource : head or msg has keywords")
                        self.news.append(News(pubDate=date, symbole=symbole, publication=head, pubSource="Reuters"))
            except:
                pass # explicative line or empty
        f.close()
        MessageManager.debugMessage("ReutersNewsSource : stop reading Reuters corpus")
        MessageManager.debugMessage("ReutersNewsSource : %d news found" % len(self.news))