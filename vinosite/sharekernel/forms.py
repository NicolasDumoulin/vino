# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 13:49:04 2015

@author: sophie.martin
"""

from django import forms
from models import ViabilityProblem

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

class TrajForm(forms.Form):
    controlInput = forms.CharField(label = '(time,control value)',initial = 'essai')
    
class ViabilityProblemForm(forms.ModelForm):
    class Meta:
        model = ViabilityProblem
        exclude = ['category']
        
class MetadataFromListForm(forms.Form):
    def __init__(self, metadata, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # now we add each metadata individually
        for metadata in metadata:
             self.fields[metadata] = forms.CharField(label=metadata)
