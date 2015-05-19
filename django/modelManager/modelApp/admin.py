from django.contrib import admin

# Register your models here.
from .models import PredictModel
from .models import Entry
from .models import Symbole
from .models import Keyword

admin.site.register(PredictModel)
admin.site.register(Entry)
admin.site.register(Symbole)
admin.site.register(Keyword)