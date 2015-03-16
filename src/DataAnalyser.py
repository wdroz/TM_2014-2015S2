# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 08:29:19 2015

@author: droz
"""

import matplotlib.pyplot as plt
from numpy import array

class DataAnalyzerLocal(object):
    def __init__(self):
        self.features = []
        self.endToEnd = []
        self.polarities = []
        self.nbDoubleChecked = 0
        self.nbFeatures = 0
    
    def addFeature(self, feature):
        try:
            if(feature.isDoubleCheckedN(0)):
                self.nbDoubleChecked += 1
            self.features.append(feature)               
            self.polarities.append(feature.polarity)
            self.endToEnd.append(feature.marketChange[0])
            self.nbFeatures += 1
        except:
            pass # not market values
        
    def plot(self):
        correlation = float(self.nbDoubleChecked)/self.nbFeatures
        print('correlation : %f' % correlation)
        #plt.hist(array(self.endToEnd), bins=20)
        plt.hist([array(self.endToEnd), array(self.polarities)], bins=2)
        plt.show()