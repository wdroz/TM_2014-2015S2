# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:55:38 2015

@author: droz
"""

from DataManager import GoogleFinanceNewsSource, GoogleFinanceMarketSource

if __name__ == "__main__":
    gfns = GoogleFinanceNewsSource()
    gfns.lookingAt('NASDAQ:GOOG','2000-01-01','2015-03-03')
    
    gfms = GoogleFinanceMarketSource()
    gfms.addMarketStatusToNews(gfns.news)
    print(str(gfns))