from django.shortcuts import render
from modelApp.models import PredictModel
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'index.html', {})
    
def showModels(request):
    myPredictModels = PredictModel.objects.all()
    return render(request, 'showmodels.html', {'models' : myPredictModels})
    
def prediction(request, model_name):
    if(model_name == None):
        return showModels(request)
    try:
        myPredictModel = PredictModel.objects.get(name=model_name)
    except:
        return showModels(request) # TODO better error
    return render(request, 'prediction.html', {'model' : myPredictModel})