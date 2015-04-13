# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 14:57:58 2015

@author: droz
"""

class DataClassifierV2(object):
        pass

class DecisionTreeWrapper(object):
    def __init__(self, **kwargs):
        self.classifier = kwargs['classifier']
        self.trainParameters = kwargs['trainParameters']
    
    def train(self, dataset):
        self.model = self.classifier.trainClassifier(dataset, **self.trainParameters)
        return self
        
    def predict(self, vect):
        return self.model.predict(vect)
        

class ClassifiersWrapper(object):
    '''
    Classe for use multiple classifier like one
    '''
    def __init__(self):
        self.classifiers = []
        self.models = []
    
    def addClassifier(self, **kwargs):
        try:
            classifier = kwargs['classifier']
            trainParameters = kwargs['trainParameters']
            weight = kwargs['weight']
            self.classifiers.append((classifier, trainParameters, weight))
        except:
            pass
        
    def train(self, dataset):
        for (classifier, trainParameters, weight) in self.classifiers:
            model = classifier.train(dataset, **trainParameters)
            self.models.append((model, weight))
            
        return self
        
    def predict(self, vect):
        predictions = {}     
        bestPred = 0
        bestPredWeight = 0
        for (model, weight) in self.models:
            res = model.predict(vect)
            if res not in predictions:
                predictions[str(res)] = 0
            predictions[str(res)] += weight
            if(predictions[str(res)] > bestPredWeight):
                bestPredWeight = predictions[str(res)]
                bestPred = res
        return bestPred
            
        