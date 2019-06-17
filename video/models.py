from django.db import models
from problem.models import Problem
from account.models import User                        
from utils.models import RichTextField

class ProblemSolution(models.Model):
    # 视频题解
    video_solution = models.FileField(blank=True, null=True, upload_to="solution_video/")
    # 文字题解
    text_solution = RichTextField(blank=True, null=True)
    # 关联题目
    problem = models.ForeignKey(Problem, null=False, on_delete=models.CASCADE, 
                                related_name="solution_video")
    # 创建信息
    timestamp = models.DateTimeField(auto_now_add=True)