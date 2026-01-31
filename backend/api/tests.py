
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import pandas as pd
import io

class UploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_upload_logic(self):
        data = {
            'Equipment Name': ['Tank A', 'Reactor B'],
            'Type': ['Tank', 'Reactor'],
            'Flowrate': [100, 250],
            'Pressure': [50, 120],  # 120 is Critical > 80
            'Temperature': [60, 180] # 180 is Critical > 150
        }
        df = pd.DataFrame(data)
        csv_file = io.StringIO()
        df.to_csv(csv_file, index=False)
        csv_file.seek(0)
        
        # We need BytesIO for file upload simulation in tests sometimes, but StringIO might work depending on parser.
        # Let's use BytesIO to be safe as the view reads it.
        byte_file = io.BytesIO(csv_file.getvalue().encode('utf-8'))
        byte_file.name = 'test.csv'

        response = self.client.post('/api/upload/', {'file': byte_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('health_score', response.data)
        self.assertIn('critical_items', response.data)
        
        # Check logic
        # 1 Critical item (Reactor B)
        self.assertEqual(len(response.data['critical_items']), 1)
        self.assertEqual(response.data['critical_items'][0]['Equipment Name'], 'Reactor B')
        
        print("Upload Logic Test Passed!")
