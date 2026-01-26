from rest_framework import serializers
from .models import UploadHistory

class UploadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadHistory
        fields = '__all__'
