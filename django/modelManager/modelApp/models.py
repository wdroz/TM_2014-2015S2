from django.db import models

# Create your models here.
class PredictModel(models.Model):
    name = models.CharField(max_length=200)
    isTrained = models.BooleanField()
    def __unicode__(self):
        return self.name
    
class Entry(models.Model):
    name = models.CharField(max_length=200)
    predictModel = models.ForeignKey(PredictModel)
    def __unicode__(self):
        return self.name
    
class Symbole(models.Model):
    symbole = models.CharField(max_length=200)
    entry = models.ForeignKey(Entry)
    def __unicode__(self):
        return self.symbole
    
class Keyword (models.Model):
    keyword = models.CharField(max_length=200)
    entry = models.ForeignKey(Entry)
    def __unicode__(self):
        return self.keyword
    
class PredictGraph(models.Model):
    name = models.CharField(max_length=200)
    predictModel = models.ForeignKey(PredictModel)
    symbole = models.CharField(max_length=200)
    def __unicode__(self):
        return 'graph for %s with %s' % (self.predictModel.name, self.symbole)
        
class PredictPoint(models.Model):
    # TODO check format
    newsPubDate = models.DateTimeField()
    newsSource = models.CharField(max_length=200)
    newsText = models.TextField()
    predictScore = models.FloatField()
    predictGraph = models.ForeignKey(PredictGraph)
    def __unicode__(self):
        return '[%s]news from %s : %s... with score %f' % (str(self.newsPubDate), self.newsSource, self.newsText[:50], self.predictScore)