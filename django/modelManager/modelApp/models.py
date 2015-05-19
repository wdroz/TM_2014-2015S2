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
    