# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:07:02 2015

@author: droz
"""
#from pyspark.mllib.classification import SVMWithSGD
import random
from numpy import mean
from MessageManager import MessageManager
import pickle
from copy import deepcopy

class DataClassifier(object):
    '''
    Classe qui permet de classifier des données à l'aide d'un classifier
    '''
    def __init__(self, dataset, classifier):
        self.dataset = dataset
        self.classifier = classifier
        self.model = None
        self.modelpath='model.p'
        
    def _giveTrainAndtest(self, rdds, nb):
        middle = rdds[nb] 
        leftPart = rdds[0:nb]
        rightPart = rdds[nb+1:]
        left = None
        right = None
        if(leftPart != []):
            left = reduce(lambda x,y : x.union(y), leftPart)
        if(rightPart != []):
            right = reduce(lambda x,y : x.union(y), rightPart)
            
        if(left == None):
            return right, middle
        if(right == None):
            return left, middle
        
        return left.union(right), middle
        
    def crossvalidation(self, nbSplits=5):
        '''
        return precision min, precision max, moyenne des precisions
        '''
        precMin = 1.0
        precMax = 0.0
        prec = 0.0
        listPrec = []
        aSplit = [1 for x in range(0,nbSplits)]
        rdds = self.dataset.randomSplit(aSplit,random.randint(1,100000))
        for cpt in range(0, nbSplits):
            MessageManager.debugMessage("DataClassifier : start new cross-validation iteration %d/%d" % (cpt, nbSplits))
            trainSet ,testSet = self._giveTrainAndtest(rdds, cpt)
            #one = trainSet.take(1)[0]
            #print('size of vect : %d' % len(one.features))
            print('trainset size : %d' % trainSet.count())
            print('testset size : %d' % testSet.count())
            # cheat because we can't use self.predict in a map here...
            toto = DataClassifier(None,self.classifier)            
            toto.train(trainSet)
            evaluatorRdd = testSet.map(lambda p: (p.label, toto.predict(p.features)))
            #evaluatorRdd = testSet.map(lambda p: (p.label, 1))
            print('evaluatorRdd size : %d' % evaluatorRdd.count())
            rddOK = evaluatorRdd.filter(lambda (a, b): a == b)
            nbOK = rddOK.count()
            nbTOT = testSet.count()
            prec = nbOK/float(nbTOT)
            if(prec < precMin):
                precMin = prec
            if(prec > precMax):
                precMax = prec
            listPrec.append(prec)
            print('iteration precision : %f' % prec)
        return precMin, precMax, mean(listPrec)
    
    def train(self, trainingSet):
        self.model = self.classifier.train(trainingSet)
    
    def predict(self, feature):
        return self.model.predict(feature)
        
    def saveModel(self):
        MessageManager.debugMessage("DataClassifier : Save Model")
        pickle.dump(self.model, open(self.modelpath, 'wb'))
    
    def loadModel(self):
        MessageManager.debugMessage("DataClassifier : Load Model")
        self.model = pickle.load(open(self.modelpath, 'rb'))
        
        
class DataClassifierEvaluator(object):
    '''
    class for evaluating classifiers
    '''
    def __init__(self, dataset):
        self.dataset = dataset
        self.classifier = []
        
    def addModel(self, classifier, name=''):
        if(name == ''):
            name = type(classifier).__name__
        self.classifier.append((classifier, name))
        
    def _giveTrainAndtest(self, rdds, nb):
        middle = rdds[nb] 
        leftPart = rdds[0:nb]
        rightPart = rdds[nb+1:]
        left = None
        right = None
        if(leftPart != []):
            left = reduce(lambda x,y : x.union(y), leftPart)
        if(rightPart != []):
            right = reduce(lambda x,y : x.union(y), rightPart)
            
        if(left == None):
            return right, middle
        if(right == None):
            return left, middle
        
        return left.union(right), middle
        
    def _results(self, evaluatorRdd):
        print('evaluatorRdd size : %d' % evaluatorRdd.count())
        rddOK = evaluatorRdd.filter(lambda (a, b): a == b)
        nbOK = rddOK.count()
        nbTOT = evaluatorRdd.count()
        prec = nbOK/float(nbTOT)
        return prec
        
    def showResultConsole(self, dicoPrec):
        bestName = ''
        bestPrec = 0.0
        for k,v in dicoPrec.items():
            print('*** Classifier %s ***' % k)
            print('\tmax\t: %f' % v['max'])
            print('\tmin\t: %f' % v['min'])
            currentMean = mean(v['mean'])
            if(currentMean > bestPrec):
                bestPrec = currentMean
                bestName = k
            print('\tmean\t: %f' % currentMean)
        print('best is %s, mean prec : %f' % (bestName, bestPrec))
        return bestName, bestPrec

    def crossvalidation(self, nbSplits=5):
        '''
        Cross validate the algorithmes for show/select the best        
        
        return best algorithme name and mean precision
        '''
        dicoPrec = {}
        for (classifier, name) in self.classifier:
            dicoPrec[name] = {'min' : 1.0, 'max' : 0.0, 'mean' : []}
        aSplit = [1 for x in range(0,nbSplits)]
        rdds = self.dataset.randomSplit(aSplit,random.randint(1,100000))
        for cpt in range(0, nbSplits):
            MessageManager.debugMessage("DataClassifierEvaluator : start new cross-validation iteration %d/%d" % (cpt+1, nbSplits))
            trainSet ,testSet = self._giveTrainAndtest(rdds, cpt)
            one = trainSet.take(1)[0]
            print('size of vect : %d' % len(one.features))
            print('trainset size : %d' % trainSet.count())
            print('testset size : %d' % testSet.count())
            for (classifier, name) in self.classifier:
                currentModel = DataClassifier(None, classifier)
                currentModel.train(trainSet)
                evaluatorRdd = testSet.map(lambda p: (p.label, currentModel.predict(p.features)))
                prec = self._results(evaluatorRdd)
                if(prec < dicoPrec[name]['min']):
                    dicoPrec[name]['min'] = prec
                if(prec > dicoPrec[name]['max']):
                    dicoPrec[name]['max'] = prec
                dicoPrec[name]['mean'].append(prec)
            print('=== Result of iteration ===')
            self.showResultConsole(dicoPrec)
        print('+++=== Final Result ===+++')
        return self.showResultConsole(dicoPrec)
        
        
    def selectBestModel(self):
        nameBest = ''
        bestPrec = 0.0
        bestClassifier = None
        for (classifier, name) in self.classifier:
            MessageManager.debugMessage('DataClassifierEvaluator : Start evaluation of %s' % name)
            dc = DataClassifier(self.dataset, classifier)
            precMin, precMax, precMean = dc.crossvalidation()
            MessageManager.debugMessage('DataClassifierEvaluator : Results for %s : \n\tPrecMin : %f\n\tPrecMax : %f\n\tPrecMean : %f' % (name, precMin, precMax, precMean))
            if(precMean > bestPrec):
                bestPrec = precMean
                nameBest = name
                bestClassifier = classifier
        MessageManager.debugMessage('DataClassifierEvaluator : best classifier is %s with precision of %f' % (nameBest, bestPrec))
        return bestClassifier, nameBest