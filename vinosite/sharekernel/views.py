from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import  ensure_csrf_cookie
from sharekernel.models import Document, ViabilityProblem, Software, Parameters,Results,ResultFormat 
from sharekernel.forms import DocumentForm, TrajForm
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.core.files import File
from operator import attrgetter
from BarGridKernel import BarGridKernel
from KdTree import KdTree
from hdf5common import HDF5Reader, HDF5Manager
from distance import Matrix, EucNorm
import FileFormatLoader
from FileFormatLoader import Loader
from KdTree import KdTree
from django.views.decorators.http import require_POST
import os
import METADATA
from django.utils import timezone
from forms import ViabilityProblemForm, MetadataFromListForm, ResultForm, ParametersForm, SoftwareForm
import humanize
import json
import tempfile
import logging

# Create your views here.

from django.http import HttpResponse


hdf5manager = HDF5Manager([BarGridKernel])
loader = Loader()

def viabilityproblem_carddata(vp):
    '''
    Build the view data for displaying an information card about a viability problem.
    '''
    resultsByFormat = {}
    resultsBySoftware = {}
    nbResults = 0
    for param in vp.parameters_set.all():
        nbResults += len(param.results_set.all())
        for result in param.results_set.all():
            resultsByFormat.setdefault(result.resultformat.title,[]).append(result)
            resultsBySoftware.setdefault(result.software,[]).append(result)

    formatsStats={f:100*float(len(results))/nbResults for f,results in resultsByFormat.iteritems()}
    softwaresStats={f:100*float(len(results))/nbResults for f,results in resultsBySoftware.iteritems()}

    return {'value':vp, 'nbResults':nbResults, 'resultsByFormat':resultsByFormat, 'formatsStats':formatsStats, 'resultsBySoftware':resultsBySoftware, 'softwaresStats':softwaresStats}

def home(request):
    context = {
        'lastkernels':Results.objects.order_by('-submissiondate')[:5],
        'lastproblems':[viabilityproblem_carddata(vp) for vp in ViabilityProblem.objects.order_by('-pk')[:5]]
        }
    return render(request, 'sharekernel/home.html', context)            
    
def visitviabilityproblems(request):
    context = {
        'viabilityproblems':ViabilityProblem.objects.all(),
        'viabilityproblemsminusfirstone':ViabilityProblem.objects.all()[1:],
        'firstviabilityproblem':ViabilityProblem.objects.all()[0],
    
        'software_list' : Software.objects.all(),

        'viabilityproblemscard':[viabilityproblem_carddata(vp) for vp in ViabilityProblem.objects.order_by('-pk')]
        }
    return render(request, 'sharekernel/visitviabilityproblems.html', context)            


def visitsoftware(request,software_id):
    a = Software.objects.get(id=software_id)
    softparval = []
    if a.parameters.split(",")[0]!="none":
        for i in range(len(a.parameters.split(","))):
            softparval.append(a.parameters.split(",")[i])

    context = {'software' : a,'softparval':softparval}
    return render(request, 'sharekernel/visitsoftware.html', context)            

def mathinfo(r):
    p = r.parameters
    if not p or not r.software:
        r=Results.objects.get(id=result_id)    
        return render(request, 'sharekernel/missingmetadata.html', {'result':r})                    
    vp = p.viabilityproblem

    stanaab = []
    connaab = []
    dynparval = []
    staconparval = []
    tarparval = []
    softparval = []
    formatparval = []
    tabvalues = []
    tabvaluesbis = []
    tabvaluesbisbis = []
    dyndes = vp.dynamicsdescription.split(",")
    index = 0
    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        stanaab.append(''.join([j[0]," : ",j[1]]))
    #    dyndes[index] = j[1]+"' = "+dyndes[index]
        index = index+1
    for i in vp.controlnameandabbreviation.split("/"):
        j = i.split(",")
        connaab.append(''.join([j[0]," : ",j[1]]))
   
    adcondes = vp.admissiblecontroldescription.split(",")
    stacondes = vp.stateconstraintdescription.split(",")
    tardes = vp.targetdescription.split(",")
    if tardes[0]=="none":
        tardes = []
 
    for i in range(len(vp.dynamicsparameters.split(","))):
        dynparval.append(''.join([vp.dynamicsparameters.split(",")[i]," = ",p.dynamicsparametervalues.split(",")[i]]))
    for i in range(len(vp.stateconstraintparameters.split(","))):
        staconparval.append(''.join([vp.stateconstraintparameters.split(",")[i]," = ",p.stateconstraintparametervalues.split(",")[i]]))
    for i in range(len(vp.targetparameters.split(","))):
        tarparval.append(''.join([vp.targetparameters.split(",")[i]," = ",p.targetparametervalues.split(",")[i]]))
    #import pdb; pdb.set_trace()
    context = {'dyndes' : dyndes, 'adcondes' : adcondes, 'stacondes' : stacondes, 'tardes' : tardes,'stanaab' : stanaab, 'connaab' : connaab, 'dynparval' : dynparval, 'staconparval' : staconparval, 'tarparval' : tarparval}
    return context

def visitresult(request,result_id):
    r = Results.objects.get(id=result_id)
    p = r.parameters
    if not p or not r.software:
        r=Results.objects.get(id=result_id)    
        return render(request, 'sharekernel/missingmetadata.html', {'result':r})                    
    vp = p.viabilityproblem
    a = r.software
    f = r.resultformat
    softparval = []
    formatparval = []

    #import pdb; pdb.set_trace()
    if a.parameters.split(",")[0]!="none":
        for i in range(min(len(a.parameters.split(",")),len(r.softwareparametervalues.split("/")))):
            softparval.append(''.join([a.parameters.split(",")[i]," = ",r.softwareparametervalues.split("/")[i]]))
    if f.parameterlist.split(";")[0]!="none":
        for i in range(len(f.parameterlist.split(";"))):
            formatparval.append(''.join([f.parameterlist.split(";")[i]," = ",r.formatparametervalues.split(";")[i]]))
    version = []
    if a.version!="none":
        version.append(a.version)
    publication = []
    if a.publication!="none":
        publication.append(a.publication)
    website = []
    if a.website!="none":
        website.append(a.website)
    contact = []
    if a.contact!="none":
        contact.append(a.contact)

#    context = {'formatparval' : formatparval,'softparval': softparval,'contact': contact,'website': website,'publication':publication,'version' : version, 'resultformat' : r.resultformat, 'viabilityproblem' : r.parameters.viabilityproblem,'result':r, 'allkernels':Results.objects.all(), 'viabilityproblem' : vp,'software' : a,'dyndes' : dyndes, 'adcondes' : adcondes, 'stacondes' : stacondes, 'tardes' : tardes,'stanaab' : stanaab, 'connaab' : connaab, 'dynparval' : dynparval, 'staconparval' : staconparval, 'tarparval' : tarparval}#,'tabvalues' : tabvalues}
    context = {'formatparval' : formatparval,'softparval': softparval,'contact': contact,'website': website,'publication':publication,'version' : version, 'resultformat' : r.resultformat, 'viabilityproblem' : r.parameters.viabilityproblem,'result':r, 'allkernels':Results.objects.all(), 'viabilityproblem' : vp,'software' : a}
    context.update(mathinfo(r))
    return render(request, 'sharekernel/visitresult.html', context)            

def visitviabilityproblem(request,viabilityproblem_id):
    vp=ViabilityProblem.objects.get(id=viabilityproblem_id)    
    stanaab = []
    connaab = []
    tabvalues = []
    tabvaluesbis = []
    tabvaluesbisbis = []

    r_list = []
    dyndes = vp.dynamicsdescription.split(",")
    index = 0
    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        if len(j)>1:
            stanaab.append(''.join([j[0]," : ",j[1]]))
 #           dyndes[index] = j[1]+"' = "+dyndes[index]
            index = index+1
    for i in vp.controlnameandabbreviation.split("/"):
        j = i.split(",")
        if len(j)>1:
            connaab.append(''.join([j[0]," : ",j[1]]))
   
    tardes = vp.targetdescription.split(",")
    if tardes[0]=="none":
        tardes = []
    p_list = vp.parameters_set.all()
    a_list = Software.objects.all()
    tabvaluesbisbis.append("Parameter Values")
    tabvaluesbis.append(tabvaluesbisbis)
    tabvaluesbisbis = []
    for a in a_list:    
        tabvaluesbisbis.append(a.title)
        tabvaluesbis.append(tabvaluesbisbis)
        tabvaluesbisbis = []
    tabvalues.append(tabvaluesbis)
    tabvaluesbis = []

    for p in p_list:
        if p.results_set.count(): # if at least one result
            tabvaluesbisbis = []
            tabvaluesbis = []
            for i in range(len(vp.dynamicsparameters.split(","))):
                tabvaluesbisbis.append(''.join([vp.dynamicsparameters.split(",")[i]," = ",p.dynamicsparametervalues.split(",")[i]]))
            for i in range(len(vp.stateconstraintparameters.split(","))):
                tabvaluesbisbis.append(''.join([vp.stateconstraintparameters.split(",")[i]," = ",p.stateconstraintparametervalues.split(",")[i]]))
            if vp.targetparameters.split(",")[0]!="none":
                for i in range(len(vp.targetparameters.split(","))):
                    tabvaluesbisbis.append(''.join([vp.targetparameters.split(",")[i]," = ",p.targetparametervalues.split(",")[i]]))
            tabvaluesbis.append(tabvaluesbisbis)
            tabvaluesbisbis = []
            for a in a_list:    
                tabvaluesbis.append(p.results_set.filter(software=a))
            tabvalues.append(tabvaluesbis)
    resultsByParameters = {}
    for parameter in p_list:
        results = []
        for result in parameter.results_set.all():
            resultData = {'value' : result, 'filesize': humanize.naturalsize(result.datafile.size)}
            results.append(resultData)
        resultsByParameters[parameter] = results
    context = {'viabilityproblem' : vp,'dyndes' : dyndes,
    'adcondes' : vp.admissiblecontroldescription.split(","),
    'stacondes' : vp.stateconstraintdescription.split(","),
    'tardes' : tardes,'stanaab' : stanaab,
    'connaab' : connaab,'tabvalues' : tabvalues,
    'resultsByParameters': resultsByParameters}
    return render(request, 'sharekernel/visitviabilityproblem.html', context)            

def kerneluploaded(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()
    else:
        form = DocumentForm() # A empty, unbound form

    return HttpResponse("Your file has been successfully uploaded")          

pspModifiedLoader = FileFormatLoader.PspModifiedLoader()
def bargrid2json(request):
    if request.method == 'POST':
        source=request.FILES['docfile'] # InMemoryUploadedFile instance
        bargrid = pspModifiedLoader.read(source)
        distancegriddimensions = [31,31] #[301,301]
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
        resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
        distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
        norm = EucNorm()
        lowborders = []    
        upborders = []    
        for i in range(len(distancegrid.dimensions)):
            lowborders.append(False)
            upborders.append(False)

        distancegrid.distance(norm,lowborders,upborders)
        data = distancegrid.toDataPointDistance()

#        insidegrid = grid.getInside()
#        minusgrid = grid.MinusBarGridKernel(insidegrid)        
        
#        out_json = json.dumps(list(resizebargrid.bars), sort_keys = True, indent = 4, ensure_ascii=False)
        
        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")

def ViNOComparison2D(request,vinoA_id,vinoB_id,ppa):
    import numpy as np
    vinos = []
    pyvinos = []
    resizebargrids = []
    minbounds = []
    maxbounds = []
    permutation = []
    if request.method == 'POST':
      vinos.append(Results.objects.get(id=vinoA_id))
      vinos.append(Results.objects.get(id=vinoB_id))
      data = [[vinos[0].resultformat.title,vinos[1].resultformat.title,'bars','bars','bars','bars','bars']]
      for vino in vinos:
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
            bargrid = hm.readKernel(vino.datafile.path)
            pyvinos.append(bargrid)
            intervalSizes = np.array(bargrid.getIntervalSizes())
            if (len(minbounds) > 0):
                minbounds = [min(minbounds[i],list(bargrid.getMinBounds())[i]) for i in range(len(minbounds))]
                maxbounds = [max(maxbounds[i],list(bargrid.getMaxBounds())[i]) for i in range(len(maxbounds))]

            else :
                minbounds = list(bargrid.getMinBounds())
	        maxbounds = list(bargrid.getMaxBounds())
            #To delete to show the original bargrid
            distancegriddimensions = [501,501]#[int(ppa),int(ppa)] #[301,301]
            distancegridintervals = map(lambda e: e-1, distancegriddimensions)
            bargridbis = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
            data.append(bargridbis.getDataToPlot())
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])
            kdt = hm.readKernel(vino.datafile.path)
            pyvinos.append(kdt)
            if (len(minbounds) > 0):
                minbounds = [min(minbounds[i],list(kdt.getMinBounds())[i]) for i in range(len(minbounds))]
                maxbounds = [max(maxbounds[i],list(kdt.getMaxBounds())[i]) for i in range(len(maxbounds))]

	    else :
	        minbounds = list(kdt.getMinBounds())
	        maxbounds = list(kdt.getMaxBounds())
            data.append(kdt.getDataToPlot())
           
      distancegriddimensions = [int(ppa),int(ppa)] #[301,301]
      distancegridintervals = map(lambda e: e-1, distancegriddimensions)
      newintervalsizes = (np.array(maxbounds)-np.array(minbounds))/np.array(distancegriddimensions)
      neworigin = list(np.array(minbounds)+newintervalsizes/2)
      newopposite = list(np.array(maxbounds)-newintervalsizes/2)


      for pyvino in pyvinos:
        if pyvino.getFormatCode() =='bars':
#            print "bargrid"
            resizebargrids.append(pyvino.toBarGridKernel(neworigin, newopposite, distancegridintervals))
#            data.append(resizebargrids[-1].getDataToPlot())
        elif pyvino.getFormatCode() =='kdtree':
#            print "kdtree"
            resizebargrids.append(pyvino.toBarGridKernel(neworigin,newopposite,distancegridintervals))
#            data.append(resizebargrids[-1].getDataToPlot())
      bb = True
      for i1 in  range(len(resizebargrids[0].permutation)):
        for i2 in  range(len(resizebargrids[0].permutation[i1])):	
	    if (resizebargrids[0].permutation[i1][i2] != resizebargrids[1].permutation[i1][i2]):
                bb = False
      if (bb == False):
        newpermutation = np.dot(resizebargrids[0].permutation,np.transpose(resizebargrids[1].permutation))
        resizebargrids.append(resizebargrids[0])
        resizebargrids[0] = resizebargrids[0].permute(newpermutation)
      data.append(resizebargrids[0].getDataToPlot())
      data.append(resizebargrids[1].getDataToPlot())
        
      aminusb = resizebargrids[0].MinusBarGridKernel(resizebargrids[1])
      bminusa = resizebargrids[1].MinusBarGridKernel(resizebargrids[0])
      ainterb = resizebargrids[0].intersectionwithBarGridKernel(resizebargrids[1])
      data.append(aminusb.getDataToPlot())
      data.append(bminusa.getDataToPlot())
      data.append(ainterb.getDataToPlot())
      out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances
      return HttpResponse(out_json)#, mimetype='text/plain')

    return HttpResponse("Nothing to do")


def ViNOView2Dancien(request,result_id,ppa):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
            bargrid = hm.readKernel(vino.datafile.path)

            distancegriddimensions = [int(ppa),int(ppa)] #[301,301]

            distancegridintervals = map(lambda e: e-1, distancegriddimensions)
            resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
            data = resizebargrid.getDataToPlot()
            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])
            kdt = hm.readKernel(vino.datafile.path)
            data = kdt.getDataToPlot()
            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')

    return HttpResponse("Nothing to do")

def ViNOView2D(request,result_id,ppa):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])

        vinopy = hm.readKernel(vino.datafile.path)
        if (int(ppa) > 0):
            distancegriddimensions = [int(ppa)]*2

            distancegridintervals = map(lambda e: e-1, distancegriddimensions)
            minbounds = list(vinopy.getMinBounds())
            maxbounds = list(vinopy.getMaxBounds())
            newintervalsizes = (np.array(maxbounds)-np.array(minbounds))/np.array(distancegriddimensions)
            neworigin = list(np.array(minbounds)+newintervalsizes/2)
            newopposite = list(np.array(maxbounds)-newintervalsizes/2)

            resizevinopy = vinopy.toBarGridKernel(neworigin,newopposite, distancegridintervals)
            data = resizevinopy.getDataToPlot()
        else :
            data = vinopy.getDataToPlot()
        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

        return HttpResponse(out_json)#, mimetype='text/plain')


    return HttpResponse("Nothing to do")

def ViNOView3D(request,result_id,ppa):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])

        vinopy = hm.readKernel(vino.datafile.path)
        if (int(ppa)>0):
            distancegriddimensions = [int(ppa)]*3
            distancegridintervals = map(lambda e: e-1, distancegriddimensions)
            minbounds = list(vinopy.getMinBounds())
            maxbounds = list(vinopy.getMaxBounds())
            newintervalsizes = (np.array(maxbounds)-np.array(minbounds))/np.array(distancegriddimensions)
            neworigin = list(np.array(minbounds)+newintervalsizes/2)
            newopposite = list(np.array(maxbounds)-newintervalsizes/2)
            resizevinopy = vinopy.toBarGridKernel(neworigin,newopposite, distancegridintervals)
        elif (vino.resultformat.title =='bars'):
            resizevinopy = vinopy
        else :
            resizevinopy = None
        if resizevinopy:
            data = resizevinopy.getDataToPlot()

            permutation = np.eye(3,dtype = int)
            permutation[0][0] = 0
            permutation[0][2] = 1
            permutation[2][0] = 1
            permutation[2][2] = 0
            data1 =resizevinopy.permute(permutation).getDataToPlot()
            permutation = np.eye(3,dtype = int)
            permutation[1][1] = 0
            permutation[1][2] = 1
            permutation[2][1] = 1
            permutation[2][2] = 0
            data2 =resizevinopy.permute(permutation).getDataToPlot()

            out_json = json.dumps(list(data+data1+data2), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances
#            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')
        else :
            data = vinopy.getDataToPlot()
            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')

    return HttpResponse("Nothing to do")

def ViNOView3Dancien(request,result_id,ppa):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
            bargrid = hm.readKernel(vino.datafile.path)
            distancegridintervals = [150]*3
            bargrid = bargrid.toBarGridKernel(bargrid.originCoords,bargrid.oppositeCoords,distancegridintervals)
            print len(bargrid.bars)
            data = bargrid.getDataToPlot()
            permutation = np.eye(3,dtype = int)
            permutation[0][0] = 0
            permutation[0][2] = 1
            permutation[2][0] = 1
            permutation[2][2] = 0
            data1 =bargrid.permute(permutation).getDataToPlot()
            permutation = np.eye(3,dtype = int)
            permutation[1][1] = 0
            permutation[1][2] = 1
            permutation[2][1] = 1
            permutation[2][2] = 0
            data2 =bargrid.permute(permutation).getDataToPlot()

            out_json = json.dumps(list(data+data1+data2), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances
#            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])
            kdtree = hm.readKernel(vino.datafile.path)
            data = kdtree.getDataToPlot()
            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')

    return HttpResponse("Nothing to do")

def ViNODistanceView(request,result_id,ppa,permutnumber):
    ''' from the coding of permutnumber the state dimension must be strictly smaller than 10
    '''
    import numpy as np
    import re
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])
        vinokernel = hm.readKernel(vino.datafile.path)

        dimension = vino.parameters.viabilityproblem.statedimension
        distancegriddimensions = [int(ppa)]*dimension
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
        newintervalsizes = (np.array(vinokernel.getMaxFrameworkBounds())-np.array(vinokernel.getMinFrameworkBounds()))/np.array(distancegriddimensions)
        neworigin = list(np.array(vinokernel.getMinFrameworkBounds())+newintervalsizes/2)
        newopposite = list(np.array(vinokernel.getMaxFrameworkBounds())-newintervalsizes/2)
        resizebargrid = vinokernel.toBarGridKernel(neworigin,newopposite,distancegridintervals)
        if (int(permutnumber) > 0) :
            permutVector = list(map(int, re.findall('[0-9]', permutnumber)))
#            print permutVector 
            permutation = np.zeros(dimension * dimension,int).reshape(dimension,dimension)
            for i in range(dimension):
                permutation[i][permutVector[i]-1]=1
#            print resizebargrid.permutation
#            print permutation
            resizebargrid = resizebargrid.permute(np.dot(resizebargrid.permutation,np.transpose(permutation)))
            distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
            norm = EucNorm()
            lowborders = []    
            upborders = []    
            for i in range(len(distancegrid.dimensions)):
                lowborders.append(True)
                upborders.append(True)

            distancegrid.distance(norm,lowborders,upborders)
            data = distancegrid.toDataPointSectionDistance()

            permutOriginCoords = np.dot(resizebargrid.permutation, resizebargrid.originCoords)
            permutOppositeCoords = np.dot(resizebargrid.permutation, resizebargrid.oppositeCoords)
            permutIntervalNumberperaxis = np.dot(resizebargrid.permutation, resizebargrid.intervalNumberperaxis)
            for i in range(len(data)):
                data[i][1:-1] = permutOriginCoords[-2:]+(permutOppositeCoords[-2:]-permutOriginCoords[-2:])*data[i][1:-1]/permutIntervalNumberperaxis[-2:]
            perm = np.dot(resizebargrid.permutation,np.arange(len(resizebargrid.originCoords)))
            data = [vinokernel.getMinFrameworkBounds()+vinokernel.getMaxFrameworkBounds()+list(perm)+list(resizebargrid.originCoords)+list(resizebargrid.oppositeCoords)]+list(data)

        else :
            distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
            norm = EucNorm()
            lowborders = []    
            upborders = []    
            for i in range(len(distancegrid.dimensions)):
                lowborders.append(True)
                upborders.append(True)

            distancegrid.distance(norm,lowborders,upborders)
            data = distancegrid.toDataPointDistance()
            permutOriginCoords = np.dot(resizebargrid.permutation, resizebargrid.originCoords)
            permutOppositeCoords = np.dot(resizebargrid.permutation, resizebargrid.oppositeCoords)
            permutIntervalNumberperaxis = np.dot(resizebargrid.permutation, resizebargrid.intervalNumberperaxis)
            for i in range(len(data)):
                data[i][:-1] = permutOriginCoords+(permutOppositeCoords-permutOriginCoords)*data[i][:-1]/permutIntervalNumberperaxis
            perm = np.dot(resizebargrid.permutation,np.arange(len(resizebargrid.originCoords)))
            data = [vinokernel.getMinFrameworkBounds()+vinokernel.getMaxFrameworkBounds()+list(perm)]+list(data)

        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")



def ViNOHistogramDistance(request,result_id,ppa,hist_maxvalue):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.title =='bars':
            hm = HDF5Manager([BarGridKernel])
        elif vino.resultformat.title =='kdtree':
            hm = HDF5Manager([KdTree])
        vinokernel = hm.readKernel(vino.datafile.path)

        distancegriddimensions = [int(ppa)]*vino.parameters.viabilityproblem.statedimension
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
        newintervalsizes = (np.array(vinokernel.getMaxFrameworkBounds())-np.array(vinokernel.getMinFrameworkBounds()))/np.array(distancegriddimensions)
        neworigin = list(np.array(vinokernel.getMinFrameworkBounds())+newintervalsizes/2)
        newopposite = list(np.array(vinokernel.getMaxFrameworkBounds())-newintervalsizes/2)
        resizebargrid = vinokernel.toBarGridKernel(neworigin,newopposite,distancegridintervals)


        distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
        norm = EucNorm()
        lowborders = []    
        upborders = []    
        for i in range(len(distancegrid.dimensions)):
            lowborders.append(True)
            upborders.append(True)

        distancegrid.distance(norm,lowborders,upborders)
        data = distancegrid.toDataPointDistance()
	histo = distancegrid.histogram(20,int(hist_maxvalue))

#        insidegrid = grid.getInside()
#        minusgrid = grid.MinusBarGridKernel(insidegrid)        
        
#        out_json = json.dumps(list(resizebargrid.bars), sort_keys = True, indent = 4, ensure_ascii=False)
        
#        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

	out_json = json.dumps(histo, sort_keys = True, ensure_ascii=False)
        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")

def bargrid2jsonNew(request,result_id):
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        bargrid = hdf5manager.readKernel(vino.datafile.path)

        distancegriddimensions = [31,31] #[301,301]
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
#.kernelMinPoint
        resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
        distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
        norm = EucNorm()
        lowborders = []    
        upborders = []    
        for i in range(len(distancegrid.dimensions)):
            lowborders.append(False)
            upborders.append(False)

        distancegrid.distance(norm,lowborders,upborders)
        data = distancegrid.toDataPointDistance()

#        insidegrid = grid.getInside()
#        minusgrid = grid.MinusBarGridKernel(insidegrid)        
        
#        out_json = json.dumps(list(resizebargrid.bars), sort_keys = True, indent = 4, ensure_ascii=False)
        
#        data = [(0,0,1),(0,1,1),(1,0,1),(1,1,10)]
        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")
    
def bargrid2json2(request,hist_maxvalue):
    if request.method == 'POST':
        source=request.FILES['docfile'] # InMemoryUploadedFile instance
        bargrid = pspModifiedLoader.readFile(source)
        distancegriddimensions = [31,31] #[301,301]
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
        resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
        distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
        norm = EucNorm()
        lowborders = []    
        upborders = []    
        for i in range(len(distancegrid.dimensions)):
            lowborders.append(False)
            upborders.append(False)

        distancegrid.distance(norm,lowborders,upborders)
        data = distancegrid.toDataPointDistance()
	histo = distancegrid.histogram(12,int(hist_maxvalue))

#        insidegrid = grid.getInside()
#        minusgrid = grid.MinusBarGridKernel(insidegrid)        
        
#        out_json = json.dumps(list(resizebargrid.bars), sort_keys = True, indent = 4, ensure_ascii=False)
        
#        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

	out_json = json.dumps(histo, sort_keys = True, ensure_ascii=False)
        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")


def bargrid2json2New(request,result_id,hist_maxvalue):
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        bargrid = hdf5manager.readKernel(vino.datafile.path)
        distancegriddimensions = [31,31] #[301,301]
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
        resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
        distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
        norm = EucNorm()
        lowborders = []    
        upborders = []    
        for i in range(len(distancegrid.dimensions)):
            lowborders.append(False)
            upborders.append(False)

        distancegrid.distance(norm,lowborders,upborders)
        data = distancegrid.toDataPointDistance()
	histo = distancegrid.histogram(12,int(hist_maxvalue))

#        insidegrid = grid.getInside()
#        minusgrid = grid.MinusBarGridKernel(insidegrid)        
        
#        out_json = json.dumps(list(resizebargrid.bars), sort_keys = True, indent = 4, ensure_ascii=False)
        
#        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

	out_json = json.dumps(histo, sort_keys = True, ensure_ascii=False)
        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")

def bargrid2json3(request,hist_maxvalue):
    if request.method == 'POST':
        source=request.FILES['docfile'] # InMemoryUploadedFile instance
        bargrid = pspModifiedLoader.read(source)
        distancegriddimensions = [31,31] #[301,301]
        distancegridintervals = map(lambda e: e-1, distancegriddimensions)
        resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
	resizebargrid2 = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
        for bar in resizebargrid2.bars:
            bar[1]=bar[1]+1
            bar[2]=bar[2]-1
        minusgrid12 = resizebargrid.MinusBarGridKernel(resizebargrid2)
	distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
        norm = EucNorm()
        lowborders = []    
        upborders = []    
        for i in range(len(distancegrid.dimensions)):
            lowborders.append(False)
            upborders.append(False)

        distancegrid.distance(norm,lowborders,upborders)
        data = distancegrid.toDataPointDistance()
	histo = distancegrid.histogram(10,int(hist_maxvalue))
        histo1 = distancegrid.histogramFromBarGrid(minusgrid12,10,int(hist_maxvalue))

        limits=[]
        occurnumber = []
        occurnumber1 = []

        for key in histo.keys():
	    limits.append(histo.get(key)[0])
            occurnumber.append(histo.get(key)[1])
	    occurnumber1.append(histo1.get(key)[1])
	histoCompar = {}
	histoCompar = dict(zip(histo.keys(),zip(limits,occurnumber,occurnumber1)))
#        insidegrid = grid.getInside()
#        minusgrid = grid.MinusBarGridKernel(insidegrid)        
        
#        out_json = json.dumps(list(resizebargrid.bars), sort_keys = True, indent = 4, ensure_ascii=False)
        
#        out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

	out_json = json.dumps(histoCompar, sort_keys = True, ensure_ascii=False)
        return HttpResponse(out_json)#, mimetype='text/plain')
    return HttpResponse("Nothing to do")

@ensure_csrf_cookie
def visualizeresult(request,result_id):
#    forms = []
#    form = TrajForm()
    r=Results.objects.get(id=result_id)
    vp=r.parameters.viabilityproblem
    rf=r.resultformat
#    for i in range(vp.statedimension):
#        forms.append(TrajForm())
#    hm = HDF5Manager([BarGridKernel])
#    bargrid = hm.readKernel(r.datafile.path)

    staab = []
    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        if len(j)>1:
            staab.append(j[1])
 
    context = {'result':r,'viabilityproblem':vp,'resultformat':rf,'staab':staab} 
    context.update(mathinfo(r))
    return render(request, 'sharekernel/visualizeresult.html', context)            




@ensure_csrf_cookie
def visualizeresulttrajectories(request,result_id):
    tab = [0,0,0,0,0]
    r=Results.objects.get(id=result_id)
    vp=r.parameters.viabilityproblem
    p_list = Parameters.objects.filter(viabilityproblem=vp)
    r_list=[]
    for p in p_list:
        r_list = r_list+list(Results.objects.filter(parameters = p))
#        print r_list

    stateabbrevs = vp.stateabbreviation()
    controlabbrevs = vp.controlabbreviation()
    descon = vp.constraints()
    ldescon=len(descon)
#    rf=r.resultformat
#    hm = HDF5Manager([BarGridKernel])
#    bargrid = hm.readKernel(r.datafile.path)

    desadm = vp.admissibles()
    ldesadm = len(desadm)
    context = {'ldesadm':ldesadm,'desadm':desadm,'ldescon':ldescon,'descon' : descon,'controlabbrevs' : controlabbrevs,'stateabbrevs' : stateabbrevs,'result':r,'results':r_list,'viabilityproblem':vp} 
    return render(request, 'sharekernel/visualizeresulttrajectories.html', context)            

def visualizeresulttrajectoriesancien(request,result_id):
    from Equation import Expression
    forms = []
    form = TrajForm()
    stanaab = []
    r=Results.objects.get(id=result_id)
    vp=r.parameters.viabilityproblem
    stateabbrevs = vp.stateabbreviation()
    controlabbrevs = vp.controlabbreviation()
    rf=r.resultformat
    for i in range(vp.statedimension):
        forms.append(TrajForm())
    hm = HDF5Manager([BarGridKernel])
    bargrid = hm.readKernel(r.datafile.path)

    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        stanaab.append(j[1])

    context = {'controlabbrevs' : controlabbrevs,'stateabbrevs' : stateabbrevs,'result':r,'viabilityproblem':vp,'resultformat':rf,'stanaab':stanaab,'fn': fn,'bargrid' : bargrid,'forms' : forms} 
    return render(request, 'sharekernel/visualizeresulttrajectories.html', context)            


def compareresult(request, vinoA_id, vinoB_id):
    vinoA = Results.objects.get(id=vinoA_id)
    vinoB = Results.objects.get(id=vinoB_id)
    vpA=vinoA.parameters.viabilityproblem
    rfA=vinoA.resultformat
    vpB=vinoB.parameters.viabilityproblem
    rfB=vinoB.resultformat
    context = {'vinoA':vinoA,'viabilityproblemA':vpA,'resultformatA':rfA,'vinoB':vinoB,'viabilityproblemB':vpB,'resultformatB':rfB} 
    return render(request, 'sharekernel/compareTwoVinos.html', context)            


def compareresultbis(request, vinoA_id, vinoB_id):
    vinoA = Results.objects.get(id=vinoA_id)
    vinoB = Results.objects.get(id=vinoB_id)
    # TODO configurable new dimensions
    distancegriddimensions = [31]*vinoA.parameters.viabilityproblem.statedimension
    distancegridintervals = map(lambda e: e-1, distancegriddimensions)
    gridA = hdf5manager.readKernel(vinoA.datafile.path)
    gridA = gridA.toBarGridKernel(gridA.originCoords, gridA.oppositeCoords, distancegridintervals)
    # TODO remove this fake
    for bar in gridA.bars:
        bar[1]=bar[1]+1
        bar[2]=bar[2]-1
    gridB = hdf5manager.readKernel(vinoB.datafile.path)
    gridB = gridB.toBarGridKernel(gridB.originCoords, gridB.oppositeCoords, distancegridintervals)
    minusgridAB = gridA.MinusBarGridKernel(gridB)
    minusgridBA = gridB.MinusBarGridKernel(gridA)
    intersection = gridA.intersectionwithBarGridKernel(gridB)
    context = {
        'vinoA': vinoA, 'vinoB': vinoB
    }
    for key,grid in [['gridA',gridA], ['gridB',gridB], ['minusgridAB', minusgridAB], ['minusgridBA', minusgridBA], ['intersection', intersection]]:
        context[key] = json.dumps(list(grid.bars), sort_keys = True, ensure_ascii=False)
    return render(request, 'sharekernel/compareTwoVinos.html', context)            

def kerneluploadpage(request, parameters_id=None, software_id=None):
    '''
    Returns a form for uploading a kernel file, using jfu form plugin (through kerneluploadfile.htm template) that will give file to views.kerneluploadfile method.
    '''
    form = DocumentForm()
    context = { 'form': form,
        'parameters_id' : parameters_id,
        'software_id' : software_id,
        }
    return render(request, 'sharekernel/kernelupload.html', context)

def metadatafilespecification(request,category_id,viabilityproblem_id,parameters_id,software_id,resultformat_id):
    if category_id == 'N':
        c=False
        vp=False
        p=False
    else:
        c = get_object_or_404(Category, id=category_id)
        if viabilityproblem_id == 'N':
            vp=False
            p=False
        else:
            vp = get_object_or_404(ViabilityProblem, id=viabilityproblem_id)
            if parameters_id == 'N':
                p=False
            else:
                p = get_object_or_404(Parameters, id=parameters_id)
    if software_id == 'N':
        a=False
    else:
        a = get_object_or_404(Software, id=software_id)    
    if resultformat_id == 'N':
        f=False
    else:
        f= get_object_or_404(ResultFormat, id=resultformat_id)
    context = { 'category' : c, 'viabilityproblem' : vp ,'parameters' : p,'resultformat' : f, 'software' : a,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'software_id' : software_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/metadatafilespecification.html', context)            

def parameterslist(request,viabilityproblem_id,parameters_id,software_id,resultformat_id):
    tabvalues = []
    vp=ViabilityProblem.objects.get(id=viabilityproblem_id)
    p_list = Parameters.objects.filter(viabilityproblem=vp)
    if vp.dynamicsparameters.split(",")[0]!="none":
        for i in range(len(vp.dynamicsparameters.split(","))):
            tabvalues.append(vp.dynamicsparameters.split(",")[i])
            for p in p_list:
                tabvalues.append(p.dynamicsparametervalues.split(",")[i])
    if vp.stateconstraintparameters.split(",")[0]!="none":
        for i in range(len(vp.stateconstraintparameters.split(","))):
            tabvalues.append(vp.stateconstraintparameters.split(",")[i])
            for p in p_list:
                tabvalues.append(p.stateconstraintparametervalues.split(",")[i])
    if vp.targetparameters.split(",")[0]!="none":
        for i in range(len(vp.targetparameters.split(","))):
            tabvalues.append(vp.targetparameters.split(",")[i])
            for p in p_list:
                tabvalues.append(p.targetparametervalues.split(",")[i])

       
    context = {'n' : range(len(p_list)),'N' : len(p_list)+1,'tabvalues': tabvalues,'viabilityproblem' : vp,'parameters_list' : p_list,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'software_id' : software_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/parameterslist.html', context)            

def algorithmlist(request):
    a_list = Software.objects.all()
    context = {'software_list' : a_list}
    return render(request, 'sharekernel/algorithmlist.html', context)            

def softwarelist(request,viabilityproblem_id,parameters_id,software_id,resultformat_id):
    a_list = Software.objects.all()
    context = {'software_list' : a_list,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'software_id' : software_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/softwarelist.html', context)            

def resultformatlist(request,viabilityproblem_id,parameters_id,software_id,resultformat_id):
    f_list = ResultFormat.objects.all()
    context = {'resultformat_list' : f_list,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'software_id' : software_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/resultformatlist.html', context)            

    
def metadatafilecontent(request,viabilityproblem_id,parameters_id,software_id,resultformat_id):
    c=False
    if viabilityproblem_id == 'N':
        vp=False
    else:
        vp = get_object_or_404(ViabilityProblem, id=viabilityproblem_id)
    if parameters_id == 'N':
        p=False
    else:
        p = get_object_or_404(Parameters, id=parameters_id)
    if software_id == 'N':
        a=False
    else:
        a = get_object_or_404(Software, id=software_id)    
    if resultformat_id == 'N':
        f=False
    else:
        f= get_object_or_404(ResultFormat, id=resultformat_id)
    #13/12/1/1/1
    context = { 'viabilityproblem' : vp ,'parameters' : p,'resultformat' : f, 'software' : a}
    return render(request, 'sharekernel/content.html', context)            

def findandsaveobject(cls, metadata, foreignkeys={}, fields={}, add_metadata={}):
    '''
    Try to find object with same metadata (excluding pk and foreign keys), or return a new object.
    If foreignkeys are given as a dict (class field name, key value), they will be used for the comparison.
    If additional fields are given as a dict (field name, field value).
    If add_metadata provided, these metadata will be added if a new object is created but won't be used for the search.
    '''
    # find objects with same metadata and foreign keys
    p = [ o for o in cls.objects.all()
            if all(
#                str(metadata.get(cls.__name__.lower()+'.'+f.name)) == str(getattr(o, f.name))
                # list all model attributes except db keys
#                for f in filter(lambda f:not f.is_relation, cls._meta.fields)
                hasattr(o, k[len(cls.__name__)+1:]) and getattr(o, k[len(cls.__name__)+1:]) == v
                for k,v in metadata.iteritems()
            ) and all(getattr(o,f)==fk for f,fk in foreignkeys.iteritems())
        ]
    if not p:
        # no object found, creating a new one
        p = cls()
        # setting metadata
        for f in filter(lambda f:not f.is_relation, cls._meta.fields):
            if cls.__name__.lower()+'.'+f.name in metadata:
                setattr(p, f.name, metadata[cls.__name__.lower()+'.'+f.name])
            elif cls.__name__.lower()+'.'+f.name in add_metadata:
                setattr(p, f.name, add_metadata[cls.__name__.lower()+'.'+f.name])
            else:
                logging.getLogger(__name__).info("metadata not found: "+cls.__name__.lower()+'.'+f.name)
        # setting additional field (data file)
        for name, value in fields.iteritems():
            if isinstance(value, File):
                getattr(p,name).save(os.path.basename(value.name), value)
            else:
                setattr(p, name, value)
        # setting foreign keys
        for fn,fk in foreignkeys.iteritems():
            setattr(p, fn, fk)
        p.save()
    else :
        p=p[0]
    return p

def valcontrol(tabt,tabu,T,i):
    if (i>=len(tabt)):
        return "error"
    else :
        u =[]
        if (T==tabt[-1]):
	    u.append(tabu[-1])	
        elif (tabt[i]<=T)&(T<tabt[-1]):
            j = i
            while (T>=tabt[j+1]):
                j =j+1
            u.append(tabu[j]+(tabu[j+1]-tabu[j])*(T-tabt[j])/(tabt[j+1]-tabt[j]))
	return u

def next(state,control,dt,method,p):
    import numpy as np
    nextstate = []
    speed = []    
    dynamics = p.speed()
    vp = p.viabilityproblem
    stateabbrevs = vp.stateabbreviation()
    controlabbrevs = vp.controlabbreviation()
#    print controlabbrevs
    for dyn in dynamics:
#        print dyn
        for var in dyn:
#            print var
            if var in stateabbrevs:
                dyn[var] = state[stateabbrevs.index(var)]
            elif var in controlabbrevs:
                dyn[var] = control[controlabbrevs.index(var)]
#        print(dyn())
        speed.append(dyn())
#    print speed
#    print state
#    print dt   
    if (method == "Euler"):
        nextstate = list(dt*np.array(speed)+np.array(state))
#    print nextstate    
    return nextstate

def evolution(Tmax,dt,method,controltrajectories,startingstate,vp,p):
    statetrajectories = []
    for i in range(vp.statedimension+1):
	statetrajectories.append([])
#    print statetrajectories
    tmin = 0
    tmax = Tmax
    for ct in controltrajectories:
        if (len(ct[0])>=1):
            tmin = max (tmin,ct[0][0])
            tmax = min (tmax,ct[0][-1])

        else :
            tmin = Tmax
            tmax = 0     
    if (tmin<=tmax):
        tcurrent = tmin
        i = 1
        for s in startingstate:
            statetrajectories[i].append(s)
            i = i+1
        laststate = startingstate
        while (tcurrent <= tmax):
            statetrajectories[0].append(tcurrent)
            valcontrols = []
            
            for ct in controltrajectories:
                valcontrols = valcontrols+valcontrol(ct[0],ct[1],tcurrent,0)
            laststate = next(laststate,valcontrols,dt,method,p)
            i = 1
            for coord in laststate:
                statetrajectories[i].append(coord)
                i = i+1
            tcurrent = tcurrent + dt
#    print statetrajectories
    return statetrajectories

def viableEvolution(Tmax,dt,method,controltrajectories,startingstate,vp,p,vino,controlsteps,stateabbrevs,controlabbrevs):
    import numpy as np
    npcontrolsteps = np.array(controlsteps)
    statetrajectories = []
    for i in range(vp.statedimension+1):
	statetrajectories.append([])
#    print statetrajectories
    tmin = 0
    tmax = Tmax
    for ct in controltrajectories:
        if (len(ct[0])>=1):
            tmin = max (tmin,ct[0][0])
            tmax = min (tmax,ct[0][-1])

        else :
            tmin = Tmax
            tmax = 0     
    if (tmin<=tmax):
        tcurrent = tmin
        i = 1
        admissibles = p.admissibles()

        for s in startingstate:
            statetrajectories[i].append(s)
            i = i+1
        laststate = startingstate
        while (tcurrent <= tmax):
            statetrajectories[0].append(tcurrent)
            valcontrols = []
            
            for ct in controltrajectories:
                valcontrols = valcontrols+valcontrol(ct[0],ct[1],tcurrent,0)
             
            currentlaststate = next(laststate,valcontrols,dt,method,p)
            distance = 1
            if vino.isInSet(currentlaststate)==False:
#                print valcontrols
                bbb = True
                while bbb:  #distance<40: #a modifier quand on pourra tester si un controle est admissible
                    bbb = False
                    base = 2*distance +1
                    baseminus1 = base-1
                    tab=[0]*vp.controldimension
                    b=True
                    l=len(tab)
                    while b==True :
                        if 0 in tab or baseminus1 in tab:
#                            print tab
                            newvalcontrols = list(np.array(valcontrols)+(np.array(tab)-distance)*npcontrolsteps)
#                            print newvalcontrols
                            bb = True
                            for adm in admissibles:
                                for var in adm:
#                                    print var
                                    if var in stateabbrevs:
                                        adm[var] = laststate[stateabbrevs.index(var)]
                                    if var in controlabbrevs:
                                        adm[var] = newvalcontrols[controlabbrevs.index(var)]
                                bb= bb and adm()
#                                print bb 
                            if bb:
                                bbb = True
                                currentlaststate = next(laststate,newvalcontrols,dt,method,p)
#                                print currentlaststate
                                if vino.isInSet(currentlaststate):
                                    b=False
                                    bbb = False
#                                    print "youi"
#                                    print newvalcontrols                               
                        j=0

                        while j<l:
                            if tab[j]<(base-1):
                                tab[j]=tab[j]+1
                                j=l
                            else:
                                tab[j]=0
                                if j==(l-1):
                                    b=False
                                    distance = distance+1 
                                j=j+1
                    distance = distance +1
            if vino.isInSet(currentlaststate):
                laststate=currentlaststate
                i = 1
                for coord in laststate:
                    statetrajectories[i].append(coord)
                    i = i+1
                tcurrent = tcurrent + dt
            else:
                tcurrent = Tmax+1
                print "Can't build viable evolution"
#    print statetrajectories
    return statetrajectories


def makeEvolutionViable(request,result_id):
    if request.method == 'POST':
        import cgi
        form = cgi.FieldStorage()
        if request.POST.has_key("controlinput1"):
            r=Results.objects.get(id=result_id)
            if r.resultformat.title =='bars':
                hm = HDF5Manager([BarGridKernel])
                vino = hm.readKernel(r.datafile.path)
            elif r.resultformat.title =='kdtree':
                hm = HDF5Manager([BarGridKernel])
                vino = hm.readKernel(r.datafile.path)

            p=r.parameters
#            print "ohoh"
            vp=r.parameters.viabilityproblem
            import numpy as np
            stateabbrevs = vp.stateabbreviation()
            controlabbrevs = vp.controlabbreviation()

            controltrajectories = [];
            controlsteps = [];
            for i in range(vp.controldimension):
                t = []
	        u = []
		
                text = request.POST["controlinput"+str(i+1)]
#                print text
#                print 'youpi'
           
                donnees = text.split(")(")
                donnees[0] = donnees[0].replace("(","")
                donnees[-1] = donnees[-1].replace(")","")
                for d in donnees:
                    if (d.find(",") >= 0) : 
		        dd = d.split(",")
                        t.append(float(dd[0]))
                        u.append(float(dd[1]))
	        controltrajectories.append([t,u])
                controlsteps.append(float(request.POST["hiddencontrolstep"+str(i+1)]))
#            print controltrajectories
            Tmax = float(request.POST["horizon"])
            dt = float(request.POST["dt"])
            method = request.POST["method"]
            startingstate = []
            for i in range(vp.statedimension):
                startingstate.append(float(request.POST["startingstate"+str(i+1)]))

#            statetrajectories = evolution(Tmax,dt,method,controltrajectories,startingstate,vp,p)           
            statetrajectories = viableEvolution(Tmax,dt,method,controltrajectories,startingstate,vp,p,vino,controlsteps,stateabbrevs,controlabbrevs)           
            
            colors = np.array([1]*len(statetrajectories[1]))
            constraints = p.constraints()
            for con in constraints:
#                print con
#                print statetrajectories[0]
                for var in con:
#                    print var
                    if var in stateabbrevs:
#                        print "dedans"
                        con[var] = np.array(statetrajectories[stateabbrevs.index(var)+1])
#                print(con())
        
                colors = colors*np.array(con(),dtype=int)
            dimension = vp.statedimension
            for i in range(len(colors)):
                if (colors[i] == 1):
                    point = []
                    for j in range(dimension):
                        point.append(statetrajectories[j+1][i])
#                    print point
                    if vino.isInSet(point):
                        colors[i] = 2
            statetrajectories.insert(0,list(colors))      

#            print statetrajectories[0]
            constrainttrajectories=[]    
            eqhandconstraints = p.leftandrighthandconstraints()
#            print eqhandconstraints
            for eqhands in eqhandconstraints:
                for eqhand in eqhands :
#                    print eqhand 
                    b = 0
                    for var in eqhand:
                        b = 1
                        if var in stateabbrevs:
#                            print "dedans"
                            eqhand[var] = np.array(statetrajectories[stateabbrevs.index(var)+2])
#                    print eqhand()
                    if (b==0):
                        constrainttrajectories.append([eqhand()]*len(statetrajectories[0]))
                    else:

                        constrainttrajectories.append(list(eqhand()))
            
            out_json = json.dumps(list(statetrajectories)+constrainttrajectories, sort_keys = True, ensure_ascii=False)
#        return JsonResponse([1, 2, 3], safe=False)   
            return HttpResponse(out_json)
        return HttpResponse("Pas POST")
    return HttpResponse("Pas POST")

def controltostate(request,result_id):
    if request.method == 'POST':
        import cgi
        form = cgi.FieldStorage()
        if request.POST.has_key("controlinput1"):
            r=Results.objects.get(id=result_id)
            if r.resultformat.title =='bars':
                hm = HDF5Manager([BarGridKernel])
                vino = hm.readKernel(r.datafile.path)
            elif r.resultformat.title =='kdtree':
                hm = HDF5Manager([KdTree])
                vino = hm.readKernel(r.datafile.path)

            p=r.parameters
#            print "ohoh"
            vp=r.parameters.viabilityproblem
            import numpy as np
            stateabbrevs = vp.stateabbreviation()
            controlabbrevs = vp.controlabbreviation()

            controltrajectories = [];
            controlsteps = [];
            for i in range(vp.controldimension):
                t = []
	        u = []
		
                text = request.POST["controlinput"+str(i+1)]
#                print text
#                print 'youpi'
           
                donnees = text.split(")(")
                donnees[0] = donnees[0].replace("(","")
                donnees[-1] = donnees[-1].replace(")","")
                for d in donnees:
                    if (d.find(",") >= 0) : 
		        dd = d.split(",")
                        t.append(float(dd[0]))
                        u.append(float(dd[1]))
	        controltrajectories.append([t,u])
#            print controltrajectories
            Tmax = float(request.POST["horizon"])
            dt = float(request.POST["dt"])
            method = request.POST["method"]
            startingstate = []
            for i in range(vp.statedimension):
                startingstate.append(float(request.POST["startingstate"+str(i+1)]))
            statetrajectories = evolution(Tmax,dt,method,controltrajectories,startingstate,vp,p)           
            
            colors = np.array([1]*len(statetrajectories[1]))
            constraints = p.constraints()
            for con in constraints:
#                print con
#                print statetrajectories[0]
                for var in con:
#                    print var
                    if var in stateabbrevs:
#                        print "dedans"
                        con[var] = np.array(statetrajectories[stateabbrevs.index(var)+1])
#                print(con())
        
                colors = colors*np.array(con(),dtype=int)
            dimension = vp.statedimension
            for i in range(len(colors)):
                if (colors[i] == 1):
                    point = []
                    for j in range(dimension):
                        point.append(statetrajectories[j+1][i])
#                    print point
                    if vino.isInSet(point):
                        colors[i] = 2
            statetrajectories.insert(0,list(colors))      

#            print statetrajectories[0]
            constrainttrajectories=[]    
            eqhandconstraints = p.leftandrighthandconstraints()
#            print eqhandconstraints
            for eqhands in eqhandconstraints:
                for eqhand in eqhands :
#                    print eqhand 
                    b = 0
                    for var in eqhand:
                        b = 1
                        if var in stateabbrevs:
#                            print "dedans"
                            eqhand[var] = np.array(statetrajectories[stateabbrevs.index(var)+2])
#                    print eqhand()
                    if (b==0):
                        constrainttrajectories.append([eqhand()]*len(statetrajectories[0]))
                    else:

                        constrainttrajectories.append(list(eqhand()))
            
            out_json = json.dumps(list(statetrajectories)+constrainttrajectories, sort_keys = True, ensure_ascii=False)
#        return JsonResponse([1, 2, 3], safe=False)   
            return HttpResponse(out_json)
        return HttpResponse("Pas POST")
    return HttpResponse("Pas POST")
    
def results_tree(request):
    return render(request, 'sharekernel/results_tree.html', {
        'problems':ViabilityProblem.objects.all(),
        'parameters':Parameters.objects.all(),
        'softwares':Software.objects.all(),
        'results':Results.objects.all(),
        'problemform': ViabilityProblemForm()
        })            

def newproblem(request, viabilityproblem_id=None):
    page_title = 'Create a new viability problem'
    if request.method == 'POST':
        form = ViabilityProblemForm(request.POST)
        if form.is_valid():
            problem = form.save()
            return HttpResponseRedirect(reverse('sharekernel:visitviabilityproblem', args=[problem.pk]))
    else:
        if viabilityproblem_id:
            page_title = 'Edit a viability problem'
            form = ViabilityProblemForm(instance=ViabilityProblem.objects.get(id=viabilityproblem_id))
        else:
            form = ViabilityProblemForm()
    return render(request, 'sharekernel/formTemplate.html', {'page_title': page_title,'form': form})            
     
def newsoftware(request):
    if request.method == 'POST':
        form = SoftwareForm(request.POST)
        if form.is_valid():
            software = form.save()
            # TODO redirect to a view of the submitted software
            return HttpResponseRedirect(reverse('sharekernel:home'))
    else:
        form = SoftwareForm()
    return render(request, 'sharekernel/formTemplate.html', {'page_title': 'Create a new software','form': form})            
    
def newparameters(request, viabilityproblem_id):
    vp = ViabilityProblem.objects.get(id=viabilityproblem_id)
    page_title = 'Add new parameters for the viability problem "'+vp.title+'"'
    if request.method == 'POST':
        form = ParametersForm(request.POST)
        if form.is_valid():
            parameters = form.save()
            return HttpResponseRedirect(reverse('sharekernel:visitviabilityproblem', args=[parameters.viabilityproblem.pk]))
    else:
        form = ParametersForm(initial={'viabilityproblem':vp})
    return render(request, 'sharekernel/formTemplate.html', {'page_title': page_title,'form': form})            

def editresult(request, result_id):
    if request.method == 'GET':
        result = Results.objects.get(id=result_id)
        # TODO ModelChoiceField for selecting foreign keys
        form = ResultForm(instance=result)
    elif request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            # TODO save and redirect
            return HttpResponse("OK")
    return render(request, 'sharekernel/formTemplate.html', {'page-title':'Editing result '+str(result), 'form': form})            
    
from jfu.http import upload_receive, UploadResponse

@require_POST
def kerneluploadfile(request):
    '''
    Try to record a new kernel by guessing its storage format.
    Returns an response as a dict with possible attributes:
      * 'error' if an error has occured, with the associated error message
      * 'path' the path to the file stored temporarily
      * 'metadata' metadata that has been retrieved or built
    '''
    # The assumption here is that jQuery File Upload
    # has been configured to send files one at a time.
    # If multiple files can be uploaded simulatenously,
    # 'file' may be a list of files.
    file = upload_receive(request)
    resultFormat = None
    parameters_id=request.POST['parameters_id'] # may be None
    software_id=request.POST['software_id'] # may be None
    if "metadata" in request.POST:
        # in this case, the file has already been uploaded, and now we get missing metadata
        metadata = {METADATA.resultformat_title: request.POST['format']}
        resultFormat = ResultFormat.objects.get(title=request.POST['format'])
        parameters = []
        for formatParameter in resultFormat.parameterlist.split(';'):
            if formatParameter in METADATA.values():
                metadata[formatParameter] = request.POST[formatParameter]
            parameters.append(request.POST[formatParameter])
        if len(parameters)>0:
            metadata[METADATA.results_formatparametervalues] = ";".join(parameters)
        kernel=KdTree.readViabilitree(request.POST['path'], metadata)
        tmpfilename = os.path.splitext(request.POST['userFilename'])[0]+u'.h5'
        hdf5manager.writeKernel(kernel, tmpfilename)
    elif file:
        # in this case, we receive a file that we try to read
        try:
            tmpfile = tempfile.NamedTemporaryFile(delete=False)
            tmpfilename = tmpfile.name
            for chunk in file.chunks():
                tmpfile.write(chunk)
            tmpfile.close()
            kernel = loader.load(tmpfile.name)
            if kernel:
                metadata = kernel.getMetadata()
            else:
                # try to detect viabilitree format
                try:
                    with open(tmpfile.name, 'r') as f:
                        head = []
                        # first line must contain header, so we deduce the number of columns
                        line = f.readline().split()
                        l = len(line)
                        head.append(line)
                        # reading first line of data, and checking if it is 
                        line = f.readline().split()
                        cols = map(float,line)
                        head.append(line)
                        # checking if dimensions are the same
                        if l == len(cols):
                            # seems good, now we need to ask some metadata for reading correctly the file
                            resultFormat = ResultFormat.objects.get(title="kdtree")
                            return UploadResponse( request, {
                                    'name' : os.path.basename(tmpfile.name),
                                    "path": tmpfile.name,
                                    "metadata": resultFormat.toDict(),
                                    'head': head,
                                    'metadataForm': render(request,'sharekernel/formatDetected.html',context = {
                                            'userFilename' : file.name,
                                            "path": tmpfile.name,
                                            "metadata": resultFormat.toDict(),
                                            "parameters_id": parameters_id,
                                            "software_id": software_id,
                                            'metadataForm': MetadataFromListForm(resultFormat.parameterlist.split(';')),
                                            'head': head,
                                            'format': resultFormat.title,
                                            'callback': request.POST['callback']
                                        }).content
                                })
                        #else:
                        #    return UploadResponse( request, {'error':"Numbers of columns doesn't match with 2 first lines"})                       
                except Exception as e:
                    # unable to detect a valid format so displaying the doc TODO
                    return UploadResponse( request, {"error": "No valid format.", "exception":e})                    
                return UploadResponse( request, {"error": "No valid format"})
        except Exception as e:
            return UploadResponse( request, {'error':str(e)})
    if kernel:    
            if not file:
                file = open(tmpfilename,'r')
            # kernel loaded, we bring the metadata to the user
            # we take care to not ask metadata about the results before to be sure to be able to read the file
            # for preventing bad experience if the user take time to complete useless forms
            # Version 3 Creating Result with empty foreign key and bringing editing view for this result
            fields = {
                "datafile": File(file),
                "submissiondate": timezone.now()
                }
            warnings=[]
            if parameters_id and parameters_id!="None":
                try:
                    fields["parameters"] = Parameters.objects.get(id=parameters_id)
                except Parameters.DoesNotExist:
                    warnings.append('Parameters set with id='+parameters_id+' has disappeared!')
            if software_id and software_id!="None":
                try:
                    fields["software"] = Software.objects.get(id=software_id)
                except Software.DoesNotExist:
                    warnings.append('Software with id='+software_id+' has disappeared!')
            if not resultFormat:
                try:
                    resultFormat = ResultFormat.objects.get(title=metadata[METADATA.resultformat_title])
                except ResultFormat.DoesNotExist:
                    # TODO log this error that should be fixed by administrators!
                    warnings.append('The format "'+metadata["resultformat.title"]+'" is unknown!')
            fields["resultformat"] = resultFormat
            result = findandsaveobject(Results, metadata, fields=fields)
            return UploadResponse( request, {
                'name' : os.path.basename(tmpfilename),
                'status': 'success',
                # TODO displays warnings
                'warnings': warnings,
                'pk': result.pk
            })            
    return UploadResponse( request, {'error':'No file provided'})
 