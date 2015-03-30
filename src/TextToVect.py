# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:18:40 2015

@author: droz
"""

from textblob import Word, TextBlob

import pickle

class VectorManager(object):
    '''
    class qui permet de créer et utiliser des vecteurs depuis du text
    '''
    def __init__(self, vectorModel):
        try:
            self.vectorModel = set(vectorModel)
            print('len of vector model : %s' % len(self.vectorModel))
        except:
            pass # None
        
    def save(self):
        pickle.dump(self.__dict__, open('vectorManager.p', 'wb'))
        
    def load(self):
        self.__dict__ = pickle.load(open('vectorManager.p', 'rb'))
        
    def processText(self, text):
        #dico = {}
        dataVect = []
        textBlob = TextBlob(text.upper())
        for word in sorted(self.vectorModel):
            #dico[word] = word in textBlob.words
            dataVect.append(1 if word in textBlob.words else 0)
        return dataVect
        
    def processList(self, myList):
        return self.processText(' '.join(myList))
                
            

class TextToVectSpark(object):
    '''
    class qui permet de faire les traitements nécessaire sur le text pour
    en faire un vecteur
    '''
    stopwords = set(["a", "about", "above", "above", "across", "after", "afterwards", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "via", "was", "we", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"])


    def __init__(self, n, filepath='/media/droz/KIKOOLOL HDD/Corpus/dataset/dataset.txt'):
        self.filepath = filepath
        self.n = n
    
    def toto(self, x):
        try:
            return (self.transformToWords(x), x.isGoodN(self.n))
        except:
            return None
        
    def createMonsterVector(self, rdd):
        return rdd.flatMap(lambda x:x[0]).filter(self.isNotStopWords)
    
    def vectorize(self, featuresRdd):
        dataSetOfWordsRDD = featuresRdd.map(self.toto).filter(lambda x: x != None)
        #for x in dataSetOfWordsRDD.collect():
        #    print(str(x))
            
        #x = self.createMonsterVector(dataSetOfWordsRDD).collect()
        x = []
        vectorManager = VectorManager(x)
        vectorManager.load()
        with open(self.filepath, 'w') as f:
            javaIterator = dataSetOfWordsRDD._jrdd.toLocalIterator()
            it = dataSetOfWordsRDD._collect_iterator_through_file(javaIterator)
            for y in it:
                myTuple = (vectorManager.processList(y[0]), y[1])
                f.write(str(myTuple) + '\n')
        return vectorManager
            
        #return dataSetOfWordsRDD.map(lambda y:(vectorManager.processList(y[0]),y[1]))
        
        
    def isNotStopWords(self, x):
        return x.lower() not in TextToVectSpark.stopwords    
    
    def transformToWords(self,x):
        '''
        permet d'avoir une list de mot lemmanizé
        '''
        words = []
        for word in x.textBlob.words:
            myWord = Word(word.lemmatize('v').encode('utf-8'))
            myWord = Word(myWord.lemma)
            myWord = Word(myWord.singularize().upper().encode('utf-8'))
            words.append(myWord)
        return words