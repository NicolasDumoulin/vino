# -*- coding: utf-8 -*-
"""
Created on Mon Sep 07 13:28:02 2015

@author: sophie.martin
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^compare/(?P<vinoA_id>([0-9]|N)+)/(?P<vinoB_id>([0-9]|N)+)/$', views.compareresult, name='compareresult'),
    url(r'^controltostate/(?P<result_id>([0-9]|N)+)/$', views.controltostate, name='controltostate'),
    url(r'^makeEvolutionViable/(?P<result_id>([0-9]|N)+)/$', views.makeEvolutionViable, name='makeEvolutionViable'),
    url(r'^problem/new/$', views.newproblem, name='newproblem'),
    url(r'^problem/(?P<viabilityproblem_id>([0-9]|N)+)/edit$', views.newproblem, name='editviabilityproblem'),
    url(r'^problem/(?P<viabilityproblem_id>([0-9]|N)+)/$', views.visitviabilityproblem, name='visitviabilityproblem'),
    url(r'^problem/(?P<viabilityproblem_id>([0-9]|N)+)/parameters/new/$', views.newparameters, name='newparameters'),
    url(r'^results/$', views.results_tree, name='results_tree'),
    url(r'^visitviabilityproblems/$', views.visitviabilityproblems, name='visitviabilityproblems'),
    url(r'^result/(?P<result_id>([0-9]|N)+)/edit$', views.editresult, name='editresult'),
    url(r'^result/(?P<result_id>([0-9]|N)+)/$', views.visitresult, name='visitresult'),
    url(r'^software/new/$', views.newsoftware, name='newsoftware'),
    url(r'^upload/p=(?P<parameters_id>([0-9]|N)+)/a=(?P<software_id>([0-9]|N)+)/$', views.kerneluploadpage, name='kerneluploadpage'),
    # Upload feature without parameters selected disabled
    #url(r'^upload/$', views.kerneluploadpage, name='kerneluploadpage'),
    url(r'kerneluploadfile/', views.kerneluploadfile, name = 'kerneluploadfile' ),
    url(r'^ViNOComparison2D/(?P<vinoA_id>([0-9]|N)+)/(?P<vinoB_id>([0-9]|N)+)/(?P<ppa>([0-9]|N)+)/$', views.ViNOComparison2D, name='ViNOComparison2D'),
    url(r'^ViNOView3D/(?P<result_id>([0-9]|N)+)/(?P<ppa>([0-9]|N)+)/$', views.ViNOView3D, name='ViNOView3D'),
    url(r'^ViNOView2D/(?P<result_id>([0-9]|N)+)/(?P<ppa>([0-9]|N)+)/$', views.ViNOView2D, name='ViNOView2D'),
    url(r'^ViNODistanceView/(?P<result_id>([0-9]|N)+)/(?P<ppa>([0-9]|NN)+)/(?P<permutnumber>([0-9]|NNN)+)/$', views.ViNODistanceView, name='ViNODistanceView'),
    url(r'^ViNOHistogramDistance/(?P<result_id>([0-9]|N)+)/(?P<ppa>([0-9]|N)+)/(?P<hist_maxvalue>([0-9]|N)+)/$', views.ViNOHistogramDistance, name='ViNOHistogramDistance'),
    url(r'^bargrid2json/$', views.bargrid2json, name='bargrid2json'),
    url(r'^bargrid2jsonNew/(?P<result_id>([0-9]|N)+)/$', views.bargrid2jsonNew, name='bargrid2jsonNew'),
    url(r'^bargrid2json2/(?P<hist_maxvalue>([0-9]|N)+)/$', views.bargrid2json2, name='bargrid2json2'),
    url(r'^bargrid2json2New/(?P<result_id>([0-9]|N)+)/(?P<hist_maxvalue>([0-9]|N)+)/$', views.bargrid2json2New, name='bargrid2json2New'),
    url(r'^bargrid2json3/(?P<hist_maxvalue>([0-9]|N)+)/$', views.bargrid2json3, name='bargrid2json3'),
    url(r'^kerneluploaded/$', views.kerneluploaded, name='kerneluploaded'),
    url(r'^metadatafilecontent/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<software_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.metadatafilecontent, name='metadatafilecontent'),
    url(r'^resultformatlist/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<software_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.resultformatlist, name='resultformatlist'),
    url(r'^softwarelist/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<software_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.softwarelist, name='softwarelist'),
    url(r'^parameterslist/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<software_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.parameterslist, name='parameterslist'),
    url(r'^visualizeresult/(?P<result_id>([0-9]|N)+)/$', views.visualizeresult, name='visualizeresult'),
    url(r'^visualizeresulttrajectories/(?P<result_id>([0-9]|N)+)/$', views.visualizeresulttrajectories, name='visualizeresulttrajectories'),
    url(r'^metadatafilespecification/(?P<category_id>([0-9]|N)+)/(?P<viabilityproblem_id>([0-9]|N)+)/(?P<parameters_id>([0-9]|N)+)/(?P<software_id>([0-9]|N)+)/(?P<resultformat_id>([0-9]|N)+)/$', views.metadatafilespecification, name='metadatafilespecification'),
]