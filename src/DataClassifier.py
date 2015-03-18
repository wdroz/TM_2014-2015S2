# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:07:02 2015

@author: droz
"""
from pyspark.mllib.classification import SVMWithSGD

class DataClassifier(object):
    def __init__(self):
        pass
    
    def train(self, trainingSet):
        self.svm = SVMWithSGD.train(trainingSet)
    
    def predict(self, feature):
        return self.svm.predict(feature)
        