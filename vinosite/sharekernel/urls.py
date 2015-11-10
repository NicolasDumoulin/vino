# -*- coding: utf-8 -*-
"""
Created on Mon Sep 07 13:28:02 2015

@author: sophie.martin
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^recorded/$', views.recorded, name='recorded'),
    url(r'^verify/$', views.verify, name='verify'),
    url(r'^kernelupload/$', views.kernelupload, name='kernelupload'),
    url(r'^bargrid2json/$', views.bargrid2json, name='bargrid2json'),
    url(r'^kerneluploaded/$', views.kerneluploaded, name='kerneluploaded'),
    url(r'^metadatafilecontent/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.metadatafilecontent, name='metadatafilecontent'),
    url(r'^resultformatlist/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.resultformatlist, name='resultformatlist'),
    url(r'^algorithmlist/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.algorithmlist, name='algorithmlist'),
    url(r'^parameterslist/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.parameterslist, name='parameterslist'),
    url(r'^viabilityproblemlist/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.viabilityproblemlist, name='viabilityproblemlist'),
    url(r'^visitresult/(?P<result_id>([0-9]|N)+)/$', views.visitresult, name='visitresult'),
    url(r'^visitviabilityproblem/(?P<viabilityproblem_id>([0-9]|N)+)/$', views.visitviabilityproblem, name='visitviabilityproblem'),
    url(r'^visitviabilityproblemlist/(?P<category_id>([0-9]|N)+)/$', views.visitviabilityproblemlist, name='visitviabilityproblemlist'),
    url(r'^categorylist/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.categorylist, name='categorylist'),
    url(r'^visitcategorylist/$', views.visitcategorylist, name='visitcategorylist'),
    url(r'^metadatafilespecification/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<algorithm_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.metadatafilespecification, name='metadatafilespecification'),
]