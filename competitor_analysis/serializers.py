# serializers.py
from rest_framework import serializers
from .models import CompetitorAnalysis

from .models import Competitor

class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        fields = '__all__'


class CompetitorAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorAnalysis
        fields = '__all__'
