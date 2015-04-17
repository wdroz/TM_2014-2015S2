# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 14:57:58 2015

@author: droz
"""
from pyspark.mllib.regression import LabeledPoint

class DataClassifierMultiClasses(object):
    '''
    Classe qui permet de classifier avec du multiclasse
    '''
    def __init__(self, binaryClassifier, numClasses):
        self.binaryClassifier = binaryClassifier
        self.numClasses = numClasses
        self.models = []
        self.combinaisons = []
        # Create all combinaisons for numClasses
        for a in range(numClasses):
            for b in range(a+1,numClasses):
                self.combinaisons.append((a,b))
        
    def train(self, dataset):
        datasetOnlyX = []
        # Create a dataset per classes
        for i in range(self.numClasses):
            specRdd = dataset.filter(lambda x: x.label == i)
            specRdd.cache()
            datasetOnlyX.append(specRdd)
        index = 0
        self.models = []
        for combi in self.combinaisons:
            index +=1
            a = combi[0]
            b = combi[1]
            print('train - index %02d\t(%d, %d)' % (index, a, b))
            # Convert classes by 0 and 1 for binary classification
            aRdd = datasetOnlyX[a].map(lambda x: LabeledPoint(0, x.features))
            bRdd = datasetOnlyX[b].map(lambda x: LabeledPoint(1, x.features))
            print('\tsize a : %d, size b : %s' % (aRdd.count(), bRdd.count()))
            model = self.binaryClassifier.train(aRdd.union(bRdd))
            self.models.append(model)
        return self
            
    
    def predict(self, vect):
        winner = 0
        winnerPts = 0
        predictVote = [0 for x in range(self.numClasses)]
        for index in range(len(self.combinaisons)):
            #print('predict - index %d' % index)
            combi = self.combinaisons[index]
            a = combi[0]
            b = combi[1]
            model = self.models[index]
            pred = model.predict(vect)
            if(pred == 0):
                predictVote[a] += 1
                if(predictVote[a] > winnerPts):
                    winnerPts = predictVote[a]
                    winner = a
            else:
                predictVote[b] += 1
                if(predictVote[b] > winnerPts):
                    winnerPts = predictVote[b]
                    winner = b
        return winner
        

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
            
        