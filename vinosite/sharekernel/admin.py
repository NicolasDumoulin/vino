from django.contrib import admin

# Register your models here.

from .models import Category, Algorithm, ViabilityProblem, Parameters,Results,ResultFormat,Document

admin.site.register(Category)
admin.site.register(Algorithm)
admin.site.register(ViabilityProblem)
admin.site.register(Parameters)
admin.site.register(Results)
admin.site.register(ResultFormat)
admin.site.register(Document)