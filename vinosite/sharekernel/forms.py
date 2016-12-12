# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 13:49:04 2015

@author: sophie.martin
"""

from django import forms
from models import ViabilityProblem, Results, Parameters, Algorithm

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

class ParametersSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super(ParametersSelect, self).__init__(*args, **kwargs)
        
    def render_option(self, selected_choices, option_value, option_label):
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        return u'<option value="%s"%s>%s</option>' % (option_value, selected_html, option_label)


class ResultForm(forms.ModelForm):
    class Meta:
        model=Results
        fields=('title','softwareparametervalues','formatparametervalues', 'parameters')
        # FIXME parameters doesn't have the initial value
        widgets = { 'parameters':ParametersSelect()}

class TrajForm(forms.Form):
    controlInput = forms.CharField(label = '(time,control value)',initial = 'essai')
    
class ViabilityProblemForm(forms.ModelForm):
    class Meta:
        model = ViabilityProblem
        exclude = ['category']
        
class ParametersForm(forms.ModelForm):
    class Meta:
        model = Parameters
        exclude = ['']
        widgets = {'viabilityproblem': forms.HiddenInput}

class AlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        exclude = ['']
        
class MetadataFromListForm(forms.Form):
    def __init__(self, metadata, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # now we add each metadata individually
        for metadata in metadata:
             self.fields[metadata] = forms.CharField(label=metadata)
