from django.contrib import admin

# Register your models here.

from .models import Software, ViabilityProblem, Parameters,Results,ResultFormat,Document

admin.site.register(Software)
admin.site.register(ViabilityProblem)
admin.site.register(Parameters)
admin.site.register(Results)
admin.site.register(ResultFormat)
admin.site.register(Document)