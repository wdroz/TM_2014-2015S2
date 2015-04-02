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
        
        