# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 13:49:04 2015

@author: sophie.martin
"""

from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )