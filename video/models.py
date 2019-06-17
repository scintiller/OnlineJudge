from django.db import models
from problem.models import Problem

class SolutionVideo(models.Model):
    video = models.FileField(blank=False, null=False)
    problem = models.ForeignKey(Problem, null=False, on_delete=models.CASCADE, 
                                related_name="solution_video")
    timestamp = models.DateTimeField(auto_now_add=True)