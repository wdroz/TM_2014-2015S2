from django.contrib import admin

# Register your models here.
from .models import PredictModel
from .models import Entry
from .models import Symbole
from .models import Keyword
from .models import PredictGraph
from .models import PredictPoint

admin.site.register(PredictModel)
admin.site.register(Entry)
admin.site.register(Symbole)
admin.site.register(Keyword)
admin.site.register(PredictGraph)
admin.site.register(PredictPoint)