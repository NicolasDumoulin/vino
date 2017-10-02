from django.contrib import admin

# Register your models here.

from .models import Software, ViabilityProblem, Parameters,Results,ResultFormat,Document, StateSet

# Displays additional columns in list of objects in admin area
class ViabilityProblemAdmin(admin.ModelAdmin):
    list_display=('title','statedimension','submitter')

class ResultsAdmin(admin.ModelAdmin):
    list_display=('title','resultformat','submitter')

class ParametersAdmin(admin.ModelAdmin):
    list_display=('__str__','viabilityproblem')

class StateSetAdmin(admin.ModelAdmin):
    list_display=('__str__','resultformat','parents_id')
    def parents_id(self, obj):
        return str(map(lambda x:x['id'],obj.parents.values()))


admin.site.register(Software)
admin.site.register(ViabilityProblem,ViabilityProblemAdmin)
admin.site.register(Parameters, ParametersAdmin)
admin.site.register(Results, ResultsAdmin)
admin.site.register(ResultFormat)
admin.site.register(Document)
admin.site.register(StateSet, StateSetAdmin)
