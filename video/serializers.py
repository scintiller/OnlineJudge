from rest_framework import serializers
from .models import ProblemSolution

class ProblemSolutionSerializer(serializers.ModelSerializer):
    class Meta():
        model = ProblemSolution
        fields = "__all__" 