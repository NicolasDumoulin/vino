from django.test import TestCase, Client
from sharekernel.models import Results, ViabilityProblem
from django.core.management import call_command
import re
import METADATA
import json

# Create your tests here.
class SimpleTest(TestCase):
    def setUp(self):
        call_command('init_database','--sure-delete')
        self.client = Client()

    def test_uploadwithoutfile(self):
        response = self.client.post('/kerneluploadfile/')
        self.assertEqual(response.status_code, 200)
        content = eval(response.content)
        self.assertTrue('error' in content['files'][0])

    def test_uploadkdtree(self):
        '''
        Upload a viabilitree file within its metadata in a single POST request.
        '''
        count = Results.objects.count()
        countVP = ViabilityProblem.objects.count()
        with open('../samples/bilingual-viabilitree/Bilingual21TS05dil3.dat') as f:
            data = {'callback':'fileSubmitted', 'files[]':f, 'metadata':{}}
            with open('../samples/bilingual-viabilitree/Bilingual21TS05dil3.txt') as f:
                myre = re.compile('^#([^:]*):(.*)$')
                for line in f:
                    if line.startswith('#'):
                        k, v = myre.match(line).groups()
                        data['metadata'][k.strip()] = v.strip()
            # serialize metadata for post request
            data['metadata'] = json.dumps(data['metadata'])
            response = self.client.post('/kerneluploadfile/', data=data)
            content = eval(response.content)
            data=content['files'][0]
            self.assertTrue('pk' in content['files'][0])
            self.assertEqual(content['files'][0]['status'], 'success')
            self.assertEqual(Results.objects.count(), count + 1)
            self.assertEqual(ViabilityProblem.objects.count(), countVP + 1)

    def test_uploadkdtree_withform(self):
        '''
        Upload a file in viabilitree format with same sequence as with the webform.
        It means, that first we upload the raw data. The server detect that it is
        a kdtree format file, and ask for missing metadata for loading the file.
        Then, a second request give the needed metadata.
        '''
        count = Results.objects.count()
        with open('../samples/bilingual-viabilitree/Bilingual21TS05dil3.dat') as f:
            response = self.client.post('/kerneluploadfile/', {'callback':'fileSubmitted','files[]':f})
            content = eval(response.content)
            data=content['files'][0]
            self.assertTrue('metadata' in data)
            metadata={}
            with open('../samples/bilingual-viabilitree/Bilingual21TS05dil3.txt') as f:
                myre = re.compile('^#([^:]*):(.*)$')
                for line in f:
                    if line.startswith('#'):
                        k, v = myre.match(line).groups()
                        metadata[k.strip()] = v.strip()
            for p,v in zip(data['parameterlist'],metadata['results.formatparametervalues'].split(';')):
                data[p]=v
            data['metadata'] = json.dumps(data['metadata'])
            response = self.client.post('/kerneluploadfile/', data=data)
            content=eval(response.content)
            self.assertEqual(content['files'][0]['status'], 'success')
            self.assertTrue('pk' in content['files'][0])
            self.assertEqual(Results.objects.count(), count + 1)

    def test_uploadH5(self):
        count = Results.objects.count()
        with open('../samples/lake/lake-eutrophicationp95pWN.h5') as f:
            response = self.client.post('/kerneluploadfile/', {'callback':'fileSubmitted','files[]':f})
            content = eval(response.content)
            self.assertEqual(content['files'][0]['status'], 'success')
            self.assertTrue('pk' in content['files'][0])
            self.assertEqual(Results.objects.count(), count + 1)
        with open('../samples/lake/lake-eutrophicationp95pWN.h5') as f:
            response = self.client.post('/kerneluploadfile/', {'callback':'fileSubmitted','files[]':f})
            content = eval(response.content)
            self.assertEqual(content['files'][0]['status'], 'success')
            self.assertTrue('pk' in content['files'][0])
            self.assertEqual(Results.objects.count(), count + 2)
