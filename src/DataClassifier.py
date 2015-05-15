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
            #TODO test here
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
        self.matrixConfusion = None
        
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
        
    def _meanMatrix(self, matrixList):
        nbMatrix = len(matrixList)
        newMatrix = []
        matrixSize = len(matrixList[0])
        for index in range(matrixSize):
            line = []
            for classes in range(matrixSize):
                mean = sum([x[index][classes]/float(nbMatrix) for x in matrixList])
                line.append(mean)
            newMatrix.append(line)
        return newMatrix
            
        
    def _showMatrix(self, matrix):
        matrixSize = len(matrix)
        chaine = '\t' + '\t'.join([str(x) for x in range(matrixSize)])
        chaine += '\n'
        for real in range(matrixSize):
            chaine += '%d\t' % real
            nbTrue = 0
            nbFalse = 0
            for predict in range(matrixSize):
                chaine += '%d\t' % matrix[real][predict]
                if(real == predict):
                    nbTrue += matrix[real][predict]
                else:
                    nbFalse += matrix[real][predict]
            prec = nbTrue/float(nbTrue + nbFalse)
            chaine += 'prec : %f\n' % prec
        print(chaine)
        return chaine
        
    def _determineNbClasses(self, rdd):
        try:
            return rdd.map(lambda (a,b): a).distinct().count()
        except:
            return 4 # because fuck spark
        
    def _createConfusionMatrix(self, evaluatorRdd):
        '''
        ex :
           0   1   2   3
        0 40   2   0  10
        
        1  2  38   3   2
        
        2  0   0   45  3
        
        3  3   0   12 29
        '''
        #nbClasses = 4 # TODO change me
        nbClasses = self._determineNbClasses(evaluatorRdd)
        matrix = []
        for realClasse in range(nbClasses):
            line = []
            for predictedClass in range(nbClasses):
                try:
                    line.append(evaluatorRdd.filter(lambda (a, b): a == realClasse and b == predictedClass).count())
                except:
                    line.append(0)
            matrix.append(line)
        return matrix
        
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
        matrixList = []
        for cpt in range(0, nbSplits):
            MessageManager.debugMessage("DataClassifierEvaluator : start new cross-validation iteration %d/%d" % (cpt+1, nbSplits))
            trainSet ,testSet = self._giveTrainAndtest(rdds, cpt)
            #one = trainSet.take(1)[0]
            #print('size of vect : %d' % len(one.features))
            print('trainset size : %d' % trainSet.count())
            print('testset size : %d' % testSet.count())
            for (classifier, name) in self.classifier:
                currentModel = DataClassifier(None, classifier)
                currentModel.train(trainSet)
                def f(iterator): yield ((p.label, currentModel.predict(p.features)) for p in iterator)
                #evaluatorRdd = testSet.mapPartitions(lambda p: (p.label, currentModel.predict(p.features)))
                evaluatorRdd = testSet.mapPartitions(f).flatMap(lambda x: x)
                matrix = self._createConfusionMatrix(evaluatorRdd)
                matrixList.append(matrix)
                self._showMatrix(matrix)
                prec = self._results(evaluatorRdd)
                if(prec < dicoPrec[name]['min']):
                    dicoPrec[name]['min'] = prec
                if(prec > dicoPrec[name]['max']):
                    dicoPrec[name]['max'] = prec
                dicoPrec[name]['mean'].append(prec)
            print('=== Result of iteration ===')
            self.showResultConsole(dicoPrec)
        print('+++=== mean confusion matrix ===+++')
        self.matrixConfusion = self._meanMatrix(matrixList)
        self._showMatrix(self.matrixConfusion)
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