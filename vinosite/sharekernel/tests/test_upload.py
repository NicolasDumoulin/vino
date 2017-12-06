from django.test import TestCase, Client
from sharekernel.models import Results

# Create your tests here.
class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_uploadwithoutfile(self):
        response = self.client.post('/kerneluploadfile/')
        self.assertEqual(response.status_code, 200)
        content = eval(response.content)
        self.assertTrue('error' in content['files'][0])

    def test_uploadH5(self):
        with open('../samples/lake/lake-eutrophicationp95pWN.h5') as f:
            response = self.client.post('/kerneluploadfile/', {'callback':'fileSubmitted','files[]':f})
            content = eval(response.content)
            self.assertEqual(content['files'][0]['status'], 'success')
            self.assertTrue('pk' in content['files'][0])
        with open('../samples/lake/lake-eutrophicationp95pWN.h5') as f:
            response = self.client.post('/kerneluploadfile/', {'callback':'fileSubmitted','files[]':f})
            content = eval(response.content)
            self.assertEqual(content['files'][0]['status'], 'success')
            self.assertTrue('pk' in content['files'][0])
