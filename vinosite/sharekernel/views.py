from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import  ensure_csrf_cookie
from sharekernel.models import Document, Category, ViabilityProblem, Algorithm, Parameters,Results,ResultFormat 
from sharekernel.forms import DocumentForm, TrajForm
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.core.files import File
from BarGridKernel import BarGridKernel
from KdTree import KdTree
from hdf5common import HDF5Reader, HDF5Manager
from distance import Matrix, EucNorm
from FileFormatLoader import Loader
from KdTree import KdTree
from django.views.decorators.http import require_POST
import os
import METADATA
from datetime import datetime
from forms import ViabilityProblemForm, MetadataFromListForm, ResultForm, ParametersForm

import json
import tempfile

# Create your views here.

from django.http import HttpResponse


hdf5manager = HDF5Manager([BarGridKernel])
loader = Loader()

def home(request):
    context = {
        'lastkernels':Results.objects.order_by('-submissiondate')[:5]
        }
    return render(request, 'sharekernel/home.html', context)            
    
def visitcategorylist(request):
    c_list = Category.objects.all()
    context = {'category_list' : c_list}
    return render(request, 'sharekernel/visitcategorylist.html', context)            

def visitviabilityproblemlist(request,category_id):
    c=Category.objects.get(id=category_id)    
    t = []
    t.append(c.id)
    c_list = Category.objects.all()
    vp_list = ViabilityProblem.objects.filter(category=Category.objects.get(id=category_id))
    context = {'t': t,'viabilityproblem_list' : vp_list,'category_list' : c_list}
    return render(request, 'sharekernel/visitviabilityproblemlist.html', context)            

def visitresult(request,result_id):
    r = Results.objects.get(id=result_id)
    p = r.parameters
    if not p or not r.algorithm:
        r=Results.objects.get(id=result_id)    
        return render(request, 'sharekernel/metadata.html', {'result':r})                    
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
        dyndes[index] = j[1]+"' = "+dyndes[index]
        index = index+1
    for i in vp.controlnameandabbreviation.split("/"):
        j = i.split(",")
        connaab.append(''.join([j[0]," : ",j[1]]))
   
    adcondes = vp.admissiblecontroldescription.split(",")
    stacondes = vp.stateconstraintdescription.split(",")
    tardes = vp.targetdescription.split(",")
    if tardes[0]=="none":
        tardes = []
    a = r.algorithm
    f = r.resultformat
    tabvaluesbisbis.append("Parameter Values")
    tabvaluesbis.append(tabvaluesbisbis)
    tabvaluesbisbis = []
    
    tabvaluesbisbis.append(a.name)
    tabvaluesbis.append(tabvaluesbisbis)
    tabvaluesbisbis = []
    tabvalues.append(tabvaluesbis)
    tabvaluesbis = []
 
    for i in range(len(vp.dynamicsparameters.split(","))):
        dynparval.append(''.join([vp.dynamicsparameters.split(",")[i]," = ",p.dynamicsparametervalues.split(",")[i]]))
    for i in range(len(vp.stateconstraintparameters.split(","))):
        staconparval.append(''.join([vp.stateconstraintparameters.split(",")[i]," = ",p.stateconstraintparametervalues.split(",")[i]]))
    for i in range(len(vp.targetparameters.split(","))):
        tarparval.append(''.join([vp.targetparameters.split(",")[i]," = ",p.targetparametervalues.split(",")[i]]))
    if a.softwareparameters.split(",")[0]!="none":
        for i in range(len(a.softwareparameters.split(","))):
            softparval.append(''.join([a.softwareparameters.split(",")[i]," = ",r.softwareparametervalues.split("/")[i]]))
    if f.parameterlist.split(",")[0]!="none":
        for i in range(len(f.parameterlist.split(","))):
            formatparval.append(''.join([f.parameterlist.split(",")[i]," = ",r.formatparametervalues.split("/")[i]]))

    '''
    r_list = Results.objects.filter(parameters = p)
    if r_list:
        tabvaluesbisbis = []
        tabvaluesbis = []
        for i in range(len(vp.dynamicsparameters.split(","))):
            tabvaluesbisbis.append(''.join([vp.dynamicsparameters.split(",")[i]," = ",p.dynamicsparametervalues.split(",")[i]]))
        for i in range(len(vp.stateconstraintparameters.split(","))):
            tabvaluesbisbis.append(''.join([vp.stateconstraintparameters.split(",")[i]," = ",p.stateconstraintparametervalues.split(",")[i]]))
        for i in range(len(vp.targetparameters.split(","))):
            tabvaluesbisbis.append(''.join([vp.targetparameters.split(",")[i]," = ",p.targetparametervalues.split(",")[i]]))


        tabvaluesbis.append(tabvaluesbisbis)
        tabvaluesbisbis = []
#!!!!! c est pas Results a la ligne suivante
        rr_list = Results.objects.filter(parameters = p,algorithm = a)
        tabvaluesbisbis = []
        if rr_list:
            for r in rr_list:
                tabvaluesbisbis.append(r)
        else:
            tabvaluesbisbis.append("None")
            tabvaluesbis.append(tabvaluesbisbis)
            tabvaluesbisbis = []
        tabvalues.append(tabvaluesbis)
        tabvaluesbis = []
    '''    
    version = []
    if a.version!="none":
        version.append(a.version)
    publication = []
    if a.publication!="none":
        publication.append(a.publication)
    website = []
    if a.softwarewebsite!="none":
        website.append(a.softwarewebsite)
    contact = []
    if a.softwarecontact!="none":
        contact.append(a.softwarecontact)

    context = {'formatparval' : formatparval,'softparval': softparval,'contact': contact,'website': website,'publication':publication,'version' : version, 'resultformat' : r.resultformat,'category' : r.parameters.viabilityproblem.category, 'viabilityproblem' : r.parameters.viabilityproblem,'result':r, 'allkernels':Results.objects.all(), 'viabilityproblem' : vp,'algorithm' : a,'dyndes' : dyndes, 'adcondes' : adcondes, 'stacondes' : stacondes, 'tardes' : tardes,'stanaab' : stanaab, 'connaab' : connaab, 'dynparval' : dynparval, 'staconparval' : staconparval, 'tarparval' : tarparval}#,'tabvalues' : tabvalues}
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
            dyndes[index] = j[1]+"' = "+dyndes[index]
            index = index+1
    for i in vp.controlnameandabbreviation.split("/"):
        j = i.split(",")
        if len(j)>1:
            connaab.append(''.join([j[0]," : ",j[1]]))
   
    adcondes = vp.admissiblecontroldescription.split(",")
    stacondes = vp.stateconstraintdescription.split(",")
    tardes = vp.targetdescription.split(",")
    if tardes[0]=="none":
        tardes = []
    p_list = Parameters.objects.filter(viabilityproblem=vp)
    a_list = Algorithm.objects.all()
    tabvaluesbisbis.append("Parameter Values")
    tabvaluesbis.append(tabvaluesbisbis)
    tabvaluesbisbis = []
    for a in a_list:    
        tabvaluesbisbis.append(a.name)
        tabvaluesbis.append(tabvaluesbisbis)
        tabvaluesbisbis = []
    tabvalues.append(tabvaluesbis)
    tabvaluesbis = []
 
    for p in p_list:
        r_list = Results.objects.filter(parameters = p)
        if r_list:
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
#!!!!! c est pas Results a la ligne suivante
                rr_list = Results.objects.filter(parameters = p,algorithm = a)
                tabvaluesbisbis = []
                if rr_list:
                    for r in rr_list:
                        tabvaluesbisbis.append(r)
                else:
                    tabvaluesbisbis.append("None")
                tabvaluesbis.append(tabvaluesbisbis)
                tabvaluesbisbis = []
            tabvalues.append(tabvaluesbis)
            tabvaluesbis = []    
    context = {'category' : vp.category,'viabilityproblem' : vp,'dyndes' : dyndes, 'adcondes' : adcondes, 'stacondes' : stacondes, 'tardes' : tardes,'stanaab' : stanaab, 'connaab' : connaab,'tabvalues' : tabvalues}
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


def bargrid2json(request):
    if request.method == 'POST':
        source=request.FILES['docfile'] # InMemoryUploadedFile instance
        bargrid = BarGridKernel.readPatrickSaintPierreFile(source)
#        bargrid = BarGridKernel.readPatrickSaintPierrebis('/home/sophie/vino/samples/2D_light.txt')
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
      data = [[vinos[0].resultformat.name,vinos[1].resultformat.name,'bars','bars','bars','bars','bars']]
      for vino in vinos:
        if vino.resultformat.name =='bars':
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
        elif vino.resultformat.name =='kdtree':
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


def ViNOView2D(request,result_id,ppa):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.name =='bars':
            hm = HDF5Manager([BarGridKernel])
            bargrid = hm.readKernel(vino.datafile.path)

            distancegriddimensions = [int(ppa),int(ppa)] #[301,301]

            distancegridintervals = map(lambda e: e-1, distancegriddimensions)
            resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
            data = resizebargrid.getDataToPlot()
            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')
        elif vino.resultformat.name =='kdtree':
            hm = HDF5Manager([KdTree])
            kdt = hm.readKernel(vino.datafile.path)
            data = kdt.getDataToPlot()
            out_json = json.dumps(list(data), sort_keys = True, ensure_ascii=False) #si on veut afficher les distances

            return HttpResponse(out_json)#, mimetype='text/plain')

    return HttpResponse("Nothing to do")

def ViNOView3D(request,result_id,ppa):
    import numpy as np
    if request.method == 'POST':
        vino = Results.objects.get(id=result_id)
        if vino.resultformat.name =='bars':
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
        elif vino.resultformat.name =='kdtree':
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
        if vino.resultformat.name =='bars':
            hm = HDF5Manager([BarGridKernel])
        elif vino.resultformat.name =='kdtree':
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
        if vino.resultformat.name =='bars':
            hm = HDF5Manager([BarGridKernel])
        elif vino.resultformat.name =='kdtree':
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
#        source=request.FILES['docfile'] # InMemoryUploadedFile instance
#        bargrid = BarGridKernel.readPatrickSaintPierreFile(source)
#        bargrid = BarGridKernel.readPatrickSaintPierrebis('/home/sophie/vino/samples/2D_light.txt')
        
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
        bargrid = BarGridKernel.readPatrickSaintPierreFile(source)
#        bargrid = BarGridKernel.readPatrickSaintPierrebis('/home/sophie/vino/samples/2D_light.txt')
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
#        source=request.FILES['docfile'] # InMemoryUploadedFile instance
#        bargrid = BarGridKernel.readPatrickSaintPierreFile(source)
#        bargrid = BarGridKernel.readPatrickSaintPierrebis('/home/sophie/vino/samples/2D_light.txt')

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
        bargrid = BarGridKernel.readPatrickSaintPierreFile(source)
#        bargrid = BarGridKernel.readPatrickSaintPierrebis('/home/sophie/vino/samples/2D_light.txt')
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
    forms = []
    form = TrajForm()
    stanaab = []
    r=Results.objects.get(id=result_id)
    vp=r.parameters.viabilityproblem
    c=vp.category
    rf=r.resultformat
    for i in range(vp.statedimension):
        forms.append(TrajForm())
    hm = HDF5Manager([BarGridKernel])
    bargrid = hm.readKernel(r.datafile.path)

    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        stanaab.append(j[1])

    context = {'result':r,'viabilityproblem':vp,'category':c,'resultformat':rf,'stanaab':stanaab,'bargrid' : bargrid,'forms' : forms} 
    return render(request, 'sharekernel/visualizeresult.html', context)            

def visualizeresulttrajectories(request,result_id):
    r=Results.objects.get(id=result_id)
    vp=r.parameters.viabilityproblem
    stateabbrevs = vp.stateabbreviation()
    controlabbrevs = vp.controlabbreviation()
    c=vp.category
#    rf=r.resultformat
#    hm = HDF5Manager([BarGridKernel])
#    bargrid = hm.readKernel(r.datafile.path)


    context = {'controlabbrevs' : controlabbrevs,'stateabbrevs' : stateabbrevs,'result':r,'viabilityproblem':vp,'category':c} 
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
    c=vp.category
    rf=r.resultformat
    for i in range(vp.statedimension):
        forms.append(TrajForm())
    hm = HDF5Manager([BarGridKernel])
    bargrid = hm.readKernel(r.datafile.path)

    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        stanaab.append(j[1])

    context = {'controlabbrevs' : controlabbrevs,'stateabbrevs' : stateabbrevs,'result':r,'viabilityproblem':vp,'category':c,'resultformat':rf,'stanaab':stanaab,'fn': fn,'bargrid' : bargrid,'forms' : forms} 
    return render(request, 'sharekernel/visualizeresulttrajectories.html', context)            


def compareresult(request, vinoA_id, vinoB_id):
    vinoA = Results.objects.get(id=vinoA_id)
    vinoB = Results.objects.get(id=vinoB_id)
    vpA=vinoA.parameters.viabilityproblem
    cA=vpA.category
    rfA=vinoA.resultformat
    vpB=vinoB.parameters.viabilityproblem
    cB=vpB.category
    rfB=vinoB.resultformat
    context = {'vinoA':vinoA,'viabilityproblemA':vpA,'categoryA':cA,'resultformatA':rfA,'vinoB':vinoB,'viabilityproblemB':vpB,'categoryB':cB,'resultformatB':rfB} 
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

def kerneluploadpage(request, parameters_id=None, algorithm_id=None):
    form = DocumentForm()
    context = { 'form': form,
        'parameters_id' : parameters_id,
        'algorithm_id' : algorithm_id,
        }
    return render(request, 'sharekernel/kernelupload.html', context)

def metadatafilespecification(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
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
    if algorithm_id == 'N':
        a=False
    else:
        a = get_object_or_404(Algorithm, id=algorithm_id)    
    if resultformat_id == 'N':
        f=False
    else:
        f= get_object_or_404(ResultFormat, id=resultformat_id)
    context = { 'category' : c, 'viabilityproblem' : vp ,'parameters' : p,'resultformat' : f, 'algorithm' : a,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/metadatafilespecification.html', context)            
        
def categorylist(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
    c_list = Category.objects.all()
    context = {'category_list' : c_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/categorylist.html', context)            
    
def viabilityproblemlist(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
    vp_list = ViabilityProblem.objects.filter(category=Category.objects.get(id=category_id))
    context = {'category' : Category.objects.get(id=category_id),'viabilityproblem_list' : vp_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/viabilityproblemlist.html', context)            
    
def parameterslist(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
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

       
    context = {'n' : range(len(p_list)),'N' : len(p_list)+1,'tabvalues': tabvalues,'viabilityproblem' : vp,'parameters_list' : p_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/parameterslist.html', context)            

def algorithmlist(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
    a_list = Algorithm.objects.all()
    context = {'algorithm_list' : a_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/algorithmlist.html', context)            

def resultformatlist(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
    f_list = ResultFormat.objects.all()
    context = {'resultformat_list' : f_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/resultformatlist.html', context)            

    
def metadatafilecontent(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
    if category_id == 'N':
        c=False
    else:
        c = get_object_or_404(Category, id=category_id)
    if viabilityproblem_id == 'N':
        vp=False
    else:
        vp = get_object_or_404(ViabilityProblem, id=viabilityproblem_id)
    if parameters_id == 'N':
        p=False
    else:
        p = get_object_or_404(Parameters, id=parameters_id)
    if algorithm_id == 'N':
        a=False
    else:
        a = get_object_or_404(Algorithm, id=algorithm_id)    
    if resultformat_id == 'N':
        f=False
    else:
        f= get_object_or_404(ResultFormat, id=resultformat_id)
    #13/12/1/1/1
    context = { 'category' : c, 'viabilityproblem' : vp ,'parameters' : p,'resultformat' : f, 'algorithm' : a}
    return render(request, 'sharekernel/content.html', context)            

def findandsaveobject(cls, metadata, foreignkeys={}, fields={}):
    '''
    Try to find object with same metadata, or return a new object
    '''
    # find objects with same metadata and foreign keys
    p = [ o for o in cls.objects.all()
            if all(
                str(metadata.get(cls.__name__.lower()+'.'+f.name)) == str(getattr(o, f.name))
                # list all model attributes except db keys
                for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields)
            ) and all(getattr(o,f)==fk for f,fk in foreignkeys.iteritems())
        ]
    if not p:
        # no object found, creating a new one
        p = cls()
        # setting metadata
        for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields):
            try:
                setattr(p, f.name, metadata[cls.__name__.lower()+'.'+f.name])
            except:
                print("metadata not found: "+cls.__name__.lower()+'.'+f.name)
        # setting additional field (data file)
        for fn,f in fields.iteritems():
            setattr(p, fn, f)
        # setting foreign keys
        for f,fk in foreignkeys.iteritems():
            setattr(p, f, fk)
        p.save()
    else :
        p=p[0]
    return p

def findandsaveobjectter(cls, metadata, foreignkeys={}, fields={}):
    '''
    Try to find object with same metadata, or return a new object
    '''
    # find objects with same metadata and foreign keys
    tab = []
    p = [ o for o in cls.objects.all()
            if all(
                str(metadata.get(cls.__name__.lower()+'.'+f.name)) == str(getattr(o, f.name))
                # list all model attributes except db keys
                for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields)
            ) and all(getattr(o,f)==fk for f,fk in foreignkeys.iteritems())
        ]
    for o in cls.objects.all():
        for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields):
            tab.append(metadata.get(cls.__name__.lower()+'.'+f.name))
            tab.append(str(getattr(o, f.name)))
            if tab[-2]!=tab[-1]:
                print tab[-2]
                print tab[-1]

    if not p:
        # no object found, creating a new one
        p = cls()
        # setting metadata
        for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields):
            try:
                setattr(p, f.name, metadata[cls.__name__.lower()+'.'+f.name])
            except:
                print("metadata not found: "+cls.__name__.lower()+'.'+f.name)
        # setting additional field (data file)
        for fn,f in fields.iteritems():
            setattr(p, fn, f)
        # setting foreign keys
        for f,fk in foreignkeys.iteritems():
            setattr(p, f, fk)
        p.save()
    else :
        p=p[0]
    return p

def findandsaveobjectbis(cls, metadata, foreignkeys={}, fields={}):
    '''
    Try to find object with same metadata, or return a new object
    '''
    # find objects with same metadata and foreign keys
    tab = []
    p = [ o for o in cls.objects.all()
            if all(
                metadata.get(cls.__name__.lower()+'.'+f.name) == getattr(o, f.name)
                # list all model attributes except db keys
                for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields)
            ) and all(getattr(o,f)==fk for f,fk in foreignkeys.iteritems())
        ]
    for o in cls.objects.all():
        for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields):
            tab.append(metadata.get(cls.__name__.lower()+'.'+f.name))
            tab.append(str(getattr(o, f.name)))
            if tab[-2]!=tab[-1]:
                print tab[-2]
                print tab[-1]

    if not p:
        # no object found, creating a new one
        p = cls()
        # setting metadata
        for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields):
            try:
                setattr(p, f.name, metadata[cls.__name__.lower()+'.'+f.name])
            except:
                print("metadata not found: "+cls.__name__.lower()+'.'+f.name)
        # setting additional field (data file)
        for fn,f in fields.iteritems():
            setattr(p, fn, f)
        # setting foreign keys
        for f,fk in foreignkeys.iteritems():
            setattr(p, f, fk)
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
#                print "dedans"
                dyn[var] = state[stateabbrevs.index(var)]
            elif var in controlabbrevs:
#                print "dedans"
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

def controltostate(request,result_id):
    if request.method == 'POST':
        import cgi
        form = cgi.FieldStorage()
        if request.POST.has_key("controlinput1"):
            r=Results.objects.get(id=result_id)
            if r.resultformat.name =='bars':
                hm = HDF5Manager([BarGridKernel])
                vino = hm.readKernel(r.datafile.path)
            elif r.resultformat.name =='kdtree':
                hm = HDF5Manager([BarGridKernel])
                vino = hm.readKernel(r.datafile.path)

            p=r.parameters
#            print "ohoh"
            vp=r.parameters.viabilityproblem
            import numpy as np
            stateabbrevs = vp.stateabbreviation()
            controlabbrevs = vp.controlabbreviation()

            controltrajectories = [];
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
            
            out_json = json.dumps(list(statetrajectories), sort_keys = True, ensure_ascii=False)
#        return JsonResponse([1, 2, 3], safe=False)   
            return HttpResponse(out_json)
        return HttpResponse("Pas POST")
    return HttpResponse("Pas POST")
    
def results_tree(request):
    return render(request, 'sharekernel/results_tree.html', {
        'problems':ViabilityProblem.objects.all(),
        'parameters':Parameters.objects.all(),
        'algorithms':Algorithm.objects.all(),
        'results':Results.objects.all(),
        'problemform': ViabilityProblemForm()
        })            

def newproblem(request):
    if request.method == 'POST':
        form = ViabilityProblemForm(request.POST)
        if form.is_valid():
            problem = form.save()
            return HttpResponseRedirect(reverse('sharekernel:visitviabilityproblem', args=[problem.pk]))
    else:
        form = ViabilityProblemForm()
    return render(request, 'sharekernel/formTemplate.html', {'page_title': 'Create a new viability problem','form': form})            
    
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

def result(request, result_id):
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
    algorithm_id=request.POST['algorithm_id'] # may be None
    if "metadata" in request.POST:
        # in this case, the file has already been uploaded, and now we get missing metadata
        metadata = {
            METADATA.statedimension: int(request.POST['statedimension']),
            METADATA.resultformat_name: request.POST['format'],
        }
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
                            resultFormat = ResultFormat.objects.get(name="kdtree")
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
                                            "algorithm_id": algorithm_id,
                                            'metadataForm': MetadataFromListForm(resultFormat.parameterlist.split()),
                                            'head': head,
                                            'format': resultFormat.name,
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
                "submissiondate": datetime.today()
                }
            warnings=[]
            if parameters_id:
                try:
                    fields["parameters"] = Parameters.objects.get(id=parameters_id)
                except Parameters.DoesNotExist:
                    warnings.append('Parameters set with id='+parameters_id+' has disappeared!')
            if algorithm_id:
                try:
                    fields["algorithm"] = Algorithm.objects.get(id=algorithm_id)
                except Algorithm.DoesNotExist:
                    warnings.append('Algorithm with id='+algorithm_id+' has disappeared!')
            if not resultFormat:
                try:
                    resultFormat = ResultFormat.objects.get(name=metadata[METADATA.resultformat_name])
                except ResultFormat.DoesNotExist:
                    # TODO log this error that should be fixed by administrators!
                    warnings.append('The format "'+metadata["resultformat.name"]+'" is unknown!')
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
     
def verify(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            source = newdoc.docfile
            t = [] 
            tt=[]
            for i in range(32):
                t.append(-1)
            c = Category()
            a = Algorithm()
            vp = ViabilityProblem() 
            p = Parameters()
            r = Results()    
            f = ResultFormat()    
        #    vp = c.viabilityproblem_set.create()
        #    p = vp.parameters_set.create()
            oui = -1 
            try:
        # Appeler la fonction de traitement
                for ligne in source:
                    donnees = ligne.rstrip('\n\r').split(":")
                    if ("#Category") in donnees:
                        if donnees[donnees.index("#Category")+1].isdigit() == False:
                            t[0] = 1
                            c.category_text = donnees[donnees.index("#Category")+1]
                    if ("#Title") in donnees:
                        if donnees[donnees.index("#Title")+1].isdigit() == False:
                            t[1] = 1
                            vp.title = donnees[donnees.index("#Title")+1]
                    if ("#Issue") in donnees:
                        t[2] = 1
                        vp.issue = donnees[donnees.index("#Issue")+1]
                    if ("#StateDimension") in donnees:
                        if donnees[donnees.index("#StateDimension")+1].isdigit() == True:
                            t[3] = 1
                            vp.statedimension = donnees[donnees.index("#StateDimension")+1]
                    if ("#StateNameAndAbbreviation") in donnees:
                        t[4] = 1
                        vp.statenameandabbreviation = donnees[donnees.index("#StateNameAndAbbreviation")+1]
                    if ("#ControlDimension") in donnees:
                        if donnees[donnees.index("#ControlDimension")+1].isdigit() == True:
                            t[5] = 1
                            vp.controldimension = donnees[donnees.index("#ControlDimension")+1]
                    if ("#ControlNameAndAbbreviation") in donnees:
                        t[6] = 1
                        vp.controlnameandabbreviation = donnees[donnees.index("#ControlNameAndAbbreviation")+1]
                    if ("#DynamicsDescription") in donnees:
                        t[7] = 1
                        vp.dynamicsdescription = donnees[donnees.index("#DynamicsDescription")+1]
                    if ("#AdmissibleControlDescription") in donnees:
                        t[8] = 1
                        vp.admissiblecontroldescription = donnees[donnees.index("#AdmissibleControlDescription")+1]
                    if ("#DynamicsParameters") in donnees:
                        t[9] = 1
                        vp.dynamicsparameters = donnees[donnees.index("#DynamicsParameters")+1]
                    if ("#StateConstraintDescription") in donnees:
                        t[10] = 1
                        vp.stateconstraintdescription = donnees[donnees.index("#StateConstraintDescription")+1]
                    if ("#StateConstraintParameters") in donnees:
                        t[11] = 1
                        vp.stateconstraintparameters = donnees[donnees.index("#StateConstraintParameters")+1]
                    if ("#TargetDescription") in donnees:
                        t[12] = 1
                        vp.targetdescription = donnees[donnees.index("#TargetDescription")+1]
                    if ("#TargetParameters") in donnees:
                        t[13] = 1
                        vp.targetparameters = donnees[donnees.index("#TargetParameters")+1]
         
                    if ("#DynamicsParameterValues") in donnees:
                        if len(donnees[donnees.index("#DynamicsParameterValues")+1].split(","))==len(vp.dynamicsparameters.split(",")):
                            t[14] = 1
                            p.dynamicsparametervalues = donnees[donnees.index("#DynamicsParameterValues")+1]
                    if ("#StateConstraintParameterValues") in donnees:
                        if len(donnees[donnees.index("#StateConstraintParameterValues")+1].split(","))==len(vp.stateconstraintparameters.split(",")):
                            t[15] = 1
                            p.stateconstraintparametervalues = donnees[donnees.index("#StateConstraintParameterValues")+1]
                    if ("#TargetParameterValues") in donnees:
                        if len(donnees[donnees.index("#TargetParameterValues")+1].split(","))==len(vp.targetparameters.split(",")):
                            t[16] = 1
                            p.targetparametervalues = donnees[donnees.index("#TargetParameterValues")+1]
        
                    if ("#ProgramName") in donnees:
                        if donnees[donnees.index("#ProgramName")+1].isdigit() == False:
                            t[17] = 1
                            a.name = donnees[donnees.index("#ProgramName")+1]
                    if ("#ProgramAuthor") in donnees:
                        if donnees[donnees.index("#ProgramAuthor")+1].isdigit() == False:
                            t[18] = 1
                            a.author = donnees[donnees.index("#ProgramAuthor")+1]
                    if ("#Version") in donnees:
                        t[19] = 1
                        a.version = donnees[donnees.index("#Version")+1]
                    if ("#Publication") in donnees:
                        if donnees[donnees.index("#Publication")+1].isdigit() == False:
                            t[20] = 1
                            a.publication = donnees[donnees.index("#Publication")+1]
                    if ("#SoftwareWebSite") in donnees:
                        if donnees[donnees.index("#SoftwareWebSite")+1].isdigit() == False:
                            t[21] = 1
                            a.softwarewebsite = donnees[donnees.index("#SoftwareWebSite")+1]
                    if ("#SoftwareContact") in donnees:
                        t[22] = 1
                        a.softwarecontact = donnees[donnees.index("#SoftwareContact")+1]
                    if ("#SoftwareParameters") in donnees:
                        t[23] = 1
                        a.softwareparameters = donnees[donnees.index("#SoftwareParameters")+1]
                    if ("#FormatName") in donnees:
                        t[24] = 1
                        f.name = donnees[donnees.index("#FormatName")+1]
                    if ("#FormatDescription") in donnees:
                        t[25] = 1
                        f.description = donnees[donnees.index("#FormatDescription")+1]
                    if ("#FormatParameterList") in donnees:
                        t[26] = 1
                        f.parameterlist = donnees[donnees.index("#FormatParameterList")+1]
                    if ("#ResultAuthor") in donnees:
                        t[27] = 1
                        r.author = donnees[donnees.index("#ResultAuthor")+1]
                    if ("#ResultSubmissionDate") in donnees:
                        t[28] = 1
                        r.submissiondate = donnees[donnees.index("#ResultSubmissionDate")+1]
                    if ("#ResultContactEmail") in donnees:
                        t[29] = 1
                        r.contactemail = donnees[donnees.index("#ResultContactEmail")+1]
                    if ("#SoftwareParameterValues") in donnees:
                        if len(donnees[donnees.index("#SoftwareParameterValues")+1].split(","))==len(a.softwareparameters.split(",")):
                            t[30] = 1
                            r.softwareparametervalues = donnees[donnees.index("#SoftwareParameterValues")+1]
                    if ("#FormatParameterValues") in donnees:
                        if len(donnees[donnees.index("#FormatParameterValues")+1].split("/"))==len(f.parameterlist.split(",")):
                            t[31] = 1
                            r.formatparametervalues = donnees[donnees.index("#FormatParameterValues")+1]
        
                if (-1) in t:        
                    oui = -1
                else:
                    oui = 1
                for i in range(32):
                    if t[i]==-1:
                        tt.append(i)        
            finally:          
        # Fermerture du fichier source
                source.close()                    
            if oui == 1:
                context = {'category': c,'viabilityproblem' : vp, 'parameters' : p, 'algorithm' : a, 'results' : r, 'resultformat' : f, 'form' : form, 'newdoc' : newdoc}
                return render(request, 'sharekernel/verif.html', context)            
            else:
                context = {'tt' : tt}
                return render(request, 'sharekernel/specificationerror.html', context)            
        else:
            context = {'form' : form}
            return render(request, 'sharekernel/kernelupload.html', context)            
           
def recorded(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
    source = newdoc.docfile
    t = [-1] * 32 
    c = Category()
    a = Algorithm()
    vp = ViabilityProblem() 
    p = Parameters()
    r = Results()    
    f = ResultFormat()    
#    vp = c.viabilityproblem_set.create()
#    p = vp.parameters_set.create()
    try:
# Appeler la fonction de traitement
        for ligne in source:
            donnees = ligne.rstrip('\n\r').split(":")
            if ("#Category") in donnees:
                if donnees[donnees.index("#Category")+1].isdigit() == False:
                    t[0] = 1
                    c.category_text = donnees[donnees.index("#Category")+1]
            if ("#Title") in donnees:
                if donnees[donnees.index("#Title")+1].isdigit() == False:
                    t[1] = 1
                    vp.title = donnees[donnees.index("#Title")+1]
            if ("#Issue") in donnees:
                t[2] = 1
                vp.issue = donnees[donnees.index("#Issue")+1]
            if ("#StateDimension") in donnees:
                if donnees[donnees.index("#StateDimension")+1].isdigit() == True:
                    t[3] = 1
                    vp.statedimension = donnees[donnees.index("#StateDimension")+1]
            if ("#StateNameAndAbbreviation") in donnees:
                t[4] = 1
                vp.statenameandabbreviation = donnees[donnees.index("#StateNameAndAbbreviation")+1]
            if ("#ControlDimension") in donnees:
                if donnees[donnees.index("#ControlDimension")+1].isdigit() == True:
                    t[5] = 1
                    vp.controldimension = donnees[donnees.index("#ControlDimension")+1]
            if ("#ControlNameAndAbbreviation") in donnees:
                t[6] = 1
                vp.controlnameandabbreviation = donnees[donnees.index("#ControlNameAndAbbreviation")+1]
            if ("#DynamicsDescription") in donnees:
                t[7] = 1
                vp.dynamicsdescription = donnees[donnees.index("#DynamicsDescription")+1]
            if ("#AdmissibleControlDescription") in donnees:
                t[8] = 1
                vp.admissiblecontroldescription = donnees[donnees.index("#AdmissibleControlDescription")+1]
            if ("#DynamicsParameters") in donnees:
                t[9] = 1
                vp.dynamicsparameters = donnees[donnees.index("#DynamicsParameters")+1]
            if ("#StateConstraintDescription") in donnees:
                t[10] = 1
                vp.stateconstraintdescription = donnees[donnees.index("#StateConstraintDescription")+1]
            if ("#StateConstraintParameters") in donnees:
                t[11] = 1
                vp.stateconstraintparameters = donnees[donnees.index("#StateConstraintParameters")+1]
            if ("#TargetDescription") in donnees:
                t[12] = 1
                vp.targetdescription = donnees[donnees.index("#TargetDescription")+1]
            if ("#TargetParameters") in donnees:
                t[13] = 1
                vp.targetparameters = donnees[donnees.index("#TargetParameters")+1]
 
            if ("#DynamicsParameterValues") in donnees:
                if len(donnees[donnees.index("#DynamicsParameterValues")+1].split(","))==len(vp.dynamicsparameters.split(",")):
                    t[14] = 1
                    p.dynamicsparametervalues = donnees[donnees.index("#DynamicsParameterValues")+1]
            if ("#StateConstraintParameterValues") in donnees:
                if len(donnees[donnees.index("#StateConstraintParameterValues")+1].split(","))==len(vp.stateconstraintparameters.split(",")):
                    t[15] = 1
                    p.stateconstraintparametervalues = donnees[donnees.index("#StateConstraintParameterValues")+1]
            if ("#TargetParameterValues") in donnees:
                if len(donnees[donnees.index("#TargetParameterValues")+1].split(","))==len(vp.targetparameters.split(",")):
                    t[16] = 1
                    p.targetparametervalues = donnees[donnees.index("#TargetParameterValues")+1]

            if ("#ProgramName") in donnees:
                if donnees[donnees.index("#ProgramName")+1].isdigit() == False:
                    t[17] = 1
                    a.name = donnees[donnees.index("#ProgramName")+1]
            if ("#ProgramAuthor") in donnees:
                if donnees[donnees.index("#ProgramAuthor")+1].isdigit() == False:
                    t[18] = 1
                    a.author = donnees[donnees.index("#ProgramAuthor")+1]
            if ("#Version") in donnees:
                t[19] = 1
                a.version = donnees[donnees.index("#Version")+1]
            if ("#Publication") in donnees:
                if donnees[donnees.index("#Publication")+1].isdigit() == False:
                    t[20] = 1
                    a.publication = donnees[donnees.index("#Publication")+1]
            if ("#SoftwareWebSite") in donnees:
                if donnees[donnees.index("#SoftwareWebSite")+1].isdigit() == False:
                    t[21] = 1
                    a.softwarewebsite = donnees[donnees.index("#SoftwareWebSite")+1]
            if ("#SoftwareContact") in donnees:
                t[22] = 1
                a.softwarecontact = donnees[donnees.index("#SoftwareContact")+1]
            if ("#SoftwareParameters") in donnees:
                t[23] = 1
                a.softwareparameters = donnees[donnees.index("#SoftwareParameters")+1]
            if ("#FormatName") in donnees:
                t[24] = 1
                f.name = donnees[donnees.index("#FormatName")+1]
            if ("#FormatDescription") in donnees:
                t[25] = 1
                f.description = donnees[donnees.index("#FormatDescription")+1]
            if ("#FormatParameterList") in donnees:
                t[26] = 1
                f.parameterlist = donnees[donnees.index("#FormatParameterList")+1]
            if ("#ResultAuthor") in donnees:
                t[27] = 1
                r.author = donnees[donnees.index("#ResultAuthor")+1]
            if ("#ResultSubmissionDate") in donnees:
                t[28] = 1
                r.submissiondate = donnees[donnees.index("#ResultSubmissionDate")+1]
            if ("#ResultContactEmail") in donnees:
                t[29] = 1
                r.contactemail = donnees[donnees.index("#ResultContactEmail")+1]
            if ("#SoftwareParameterValues") in donnees:
                if len(donnees[donnees.index("#SoftwareParameterValues")+1].split(","))==len(a.softwareparameters.split(",")):
                    t[30] = 1
                    r.softwareparametervalues = donnees[donnees.index("#SoftwareParameterValues")+1]
            if ("#FormatParameterValues") in donnees:
                if len(donnees[donnees.index("#FormatParameterValues")+1].split("/"))==len(f.parameterlist.split(",")):
                    t[31] = 1
                    r.formatparametervalues = donnees[donnees.index("#FormatParameterValues")+1]

        if -1 not in t:
            b=-1
            for cc in Category.objects.all():
                if cc.category_text == c.category_text:
                    b=1
                    bb=-1
                    for vpvp in cc.viabilityproblem_set.all():
                        if vpvp.title == vp.title:
                            bb = 1
                            bbb = -1
                            for pp in vpvp.parameters_set.all():
                                if (pp.dynamicsparametervalues == p.dynamicsparametervalues) and (pp.stateconstraintparametervalues == p.stateconstraintparametervalues) and (pp.targetparametervalues == p.targetparametervalues):
                                    bbb = 1
                                    pbis = pp
                                
                            if bbb == -1:
                                pbis = vpvp.parameters_set.create(dynamicsparametervalues = p.dynamicsparametervalues,stateconstraintparametervalues = p.stateconstraintparametervalues,targetparametervalues = p.targetparametervalues)
                                cc.save()
                            

                    if bb == -1:
                        vpbis = cc.viabilityproblem_set.create(title = vp.title, issue = vp.issue, statedimension = vp.statedimension, statenameandabbreviation = vp.statenameandabbreviation, controldimension = vp.controldimension, controlnameandabbreviation = vp.controlnameandabbreviation, dynamicsdescription = vp.dynamicsdescription, admissiblecontroldescription = vp.admissiblecontroldescription, dynamicsparameters = vp.dynamicsparameters, stateconstraintdescription = vp.stateconstraintdescription, stateconstraintparameters = vp.stateconstraintparameters, targetdescription = vp.targetdescription, targetparameters = vp.targetparameters)
                        cc.save()
                        pbis = vpbis.parameters_set.create(dynamicsparametervalues = p.dynamicsparametervalues,stateconstraintparametervalues = p.stateconstraintparametervalues,targetparametervalues = p.targetparametervalues)
                        cc.save()
            if b == -1:
                c.save()
                vpbis = c.viabilityproblem_set.create(title = vp.title, issue = vp.issue, statedimension = vp.statedimension, statenameandabbreviation = vp.statenameandabbreviation, controldimension = vp.controldimension, controlnameandabbreviation = vp.controlnameandabbreviation, dynamicsdescription = vp.dynamicsdescription, admissiblecontroldescription = vp.admissiblecontroldescription, dynamicsparameters = vp.dynamicsparameters, stateconstraintdescription = vp.stateconstraintdescription, stateconstraintparameters = vp.stateconstraintparameters, targetdescription = vp.targetdescription, targetparameters = vp.targetparameters)
                c.save()
                pbis = vpbis.parameters_set.create(dynamicsparametervalues = p.dynamicsparametervalues,stateconstraintparametervalues = p.stateconstraintparametervalues,targetparametervalues = p.targetparametervalues)
                c.save()            
            b=-1
            for aa in Algorithm.objects.all():
                if (aa.name == a.name) and (aa.version == a.version):
                    b=1
                    abis = aa
            if b == -1:
                a.save()
                abis = a         
            b=-1
            for ff in ResultFormat.objects.all():
                if ff.name == f.name:
                    b=1
                    fbis = ff
            if b == -1:
                f.save()
                fbis = f 
            pbis.results_set.create(algorithm = abis,resultformat = fbis,author = r.author,submissiondate = r.submissiondate, contactemail = r.contactemail, softwareparametervalues = r.softwareparametervalues,formatparametervalues = r.formatparametervalues, datafile = request.FILES['docfile'])
            pbis.save()
    finally:  
# Fermerture du fichier source
        source.close()            
    if -1 not in t:
        return HttpResponse("Your file has been successfully uploaded")         
    else:
        return HttpResponse("Your kernel was not uploaded.")    
        
