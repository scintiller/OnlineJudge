from rest_framework import serializers
from .models import SolutionVideo

class UploadSolutionVideoSerializer(serializers.Serializer):
    video = serializers.FileField()
    problem_id = serializers.IntegerField()


class SolutionVideoSerializer(serializers.ModelSerializer):
    class Meta():
        model = SolutionVideo
        fields = "__all__" 