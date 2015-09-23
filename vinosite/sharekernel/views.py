from django.shortcuts import get_object_or_404,render
from sharekernel.models import Document, Category, ViabilityProblem, Algorithm, Parameters,Results,ResultFormat 
from sharekernel.forms import DocumentForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.files import File

# Create your views here.

from django.http import HttpResponse



def home(request):
    context = {}
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
    vp = p.viabilityproblem    
    stanaab = []
    connaab = []
    dynparval = []
    staconparval = []
    tarparval = []
    tabvalues = []
    tabvaluesbis = []
    tabvaluesbisbis = []

    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        stanaab.append(''.join([j[0]," : ",j[1]]))
    for i in vp.controlnameandabbreviation.split("/"):
        j = i.split(",")
        connaab.append(''.join([j[0]," : ",j[1]]))
   
    dyndes = vp.dynamicsdescription.split(",")
    adcondes = vp.admissiblecontroldescription.split(",")
    stacondes = vp.stateconstraintdescription.split(",")
    tardes = vp.targetdescription.split(",")
    a = r.algorithm
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
    context = {'viabilityproblem' : vp,'algorithm' : a,'dyndes' : dyndes, 'adcondes' : adcondes, 'stacondes' : stacondes, 'tardes' : tardes,'stanaab' : stanaab, 'connaab' : connaab, 'dynparval' : dynparval, 'staconparval' : staconparval, 'tarparval' : tarparval,'tabvalues' : tabvalues}
    return render(request, 'sharekernel/visitresult.html', context)            

def visitviabilityproblem(request,viabilityproblem_id):
    vp=ViabilityProblem.objects.get(id=viabilityproblem_id)    
    stanaab = []
    connaab = []
    tabvalues = []
    tabvaluesbis = []
    tabvaluesbisbis = []

    r_list = []

    for i in vp.statenameandabbreviation.split("/"):
        j = i.split(",")
        stanaab.append(''.join([j[0]," : ",j[1]]))
    for i in vp.controlnameandabbreviation.split("/"):
        j = i.split(",")
        connaab.append(''.join([j[0]," : ",j[1]]))
   
    dyndes = vp.dynamicsdescription.split(",")
    adcondes = vp.admissiblecontroldescription.split(",")
    stacondes = vp.stateconstraintdescription.split(",")
    tardes = vp.targetdescription.split(",")
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
    context = {'viabilityproblem' : vp,'dyndes' : dyndes, 'adcondes' : adcondes, 'stacondes' : stacondes, 'tardes' : tardes,'stanaab' : stanaab, 'connaab' : connaab,'tabvalues' : tabvalues}
    return render(request, 'sharekernel/visitviabilityproblem.html', context)            

def kerneluploaded(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
#            return HttpResponseRedirect(reverse('sharekernel.views.kernelupload'))
    else:
        form = DocumentForm() # A empty, unbound form

    context = {}
    return render(request, 'sharekernel/kerneluploaded.html', context)            
    
def kernelupload(request):
    # Handle file upload
#    if request.method == 'POST':
#        form = DocumentForm(request.POST, request.FILES)
#        if form.is_valid():
#            newdoc = Document(docfile = request.FILES['docfile'])
#            newdoc.save()

            # Redirect to the document list after POST
#            return HttpResponseRedirect(reverse('sharekernel.views.kernelupload'))
#    else:
#        form = DocumentForm() # A empty, unbound form
    form = DocumentForm()
    # Load documents for the list page
#    documents = Document.objects.all()

    # Render list page with the documents and the form
#    return render_to_response(
#        'sharekernel/kernelupload.html',
#        {'documents': documents, 'form': form},
#        context_instance=RequestContext(request)
#)
#    context = {'documents': documents, 'form': form}
    context = { 'form': form}
 
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
    context = {'viabilityproblem_list' : vp_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
    return render(request, 'sharekernel/viabilityproblemlist.html', context)            
    
def parameterslist(request,category_id,viabilityproblem_id,parameters_id,algorithm_id,resultformat_id):
    p_list = Parameters.objects.filter(viabilityproblem=ViabilityProblem.objects.get(id=viabilityproblem_id))
    context = {'parameters_list' : p_list,'category_id' : category_id,'viabilityproblem_id' : viabilityproblem_id,'parameters_id' : parameters_id,'algorithm_id' : algorithm_id,'resultformat_id' : resultformat_id}
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
    
def verifyancien(request):
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()


#    source = open("dataessai.txt", "r")
    source = newdoc.docfile
    #open(newdoc.docfile.path,"r")
    t = [] 
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
 
    finally: 
 
# Fermerture du fichier source
        source.close()
        
    if oui == 1:
        context = {'category': c,'viabilityproblem' : vp, 'parameters' : p, 'algorithm' : a, 'results' : r, 'resultformat' : f}
        return render(request, 'sharekernel/verif.html', context)            
#        return HttpResponse("Your kernel has been successfully uploaded to the database.")
    else:
        return HttpResponse("Your metadata do not share the notifications.")
        
    
def verify(request):
    
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
#            newdoc.save()


        #    source = open("dataessai.txt", "r")
            source = newdoc.docfile
            #open(newdoc.docfile.path,"r")
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
        #        return HttpResponse("Your kernel has been successfully uploaded to the database.")
            else:
                context = {'tt' : tt}
                return render(request, 'sharekernel/specificationerror.html', context)            
#                return HttpResponse("Your metadata do not share the notifications.")

        else:
            context = {'form' : form}
            return render(request, 'sharekernel/kernelupload.html', context)            
            
def recorded(request):
    
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
#            newdoc.save()


#    source = open("dataessai.txt", "r")
    source = newdoc.docfile
    #open(newdoc.docfile.path,"r")
    t = [] 
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
 
        if oui == 1:
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
            
    if oui ==1:
        context = {}
        return render(request, 'sharekernel/record.html', context)            
                        
#        return HttpResponse("Your kernel has been successfully uploaded to the database.")
    else:
        return HttpResponse("Your kernel was not uploaded.")
    
def recordedancien(request):
    
    source = open("dataessai.txt", "r")
    t = [] 
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
 
    finally: 
 
# Fermerture du fichier source
        source.close()
    if oui == 1:
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


        pbis.results_set.create(algorithm = abis,resultformat = fbis,author = r.author,submissiondate = r.submissiondate, contactemail = r.contactemail, softwareparametervalues = r.softwareparametervalues,formatparametervalues = r.formatparametervalues)
        pbis.save()

            
        context = {}
        return render(request, 'sharekernel/record.html', context)            
                        
#        return HttpResponse("Your kernel has been successfully uploaded to the database.")
    else:
        return HttpResponse("Your kernel was not uploaded.")
        