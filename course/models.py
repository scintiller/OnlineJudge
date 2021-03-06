from django.db import models
from utils.models import JSONField

from account.models import User
from utils.models import RichTextField
from problem.models import Problem


class Course(models.Model):
    # 第几章
    charpter = models.TextField()
    # 第几节
    section = models.TextField()
    # 标题
    title = models.TextField()
    # 知识点总结
    content = RichTextField()
    # 题目链接
    on_class_problems = models.ManyToManyField(Problem, related_name="course_on_class_problems") 
    after_class_problems = models.ManyToManyField(Problem, related_name="course_after_class_problems")
    # 创建信息
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "course"
        ordering = ('create_time',)


class PowerPoint(models.Model):
    ppt = models.FileField(blank=False, null=False, upload_to="ppt/")
    course = models.ForeignKey(Course, null=False, on_delete=models.CASCADE, 
                                related_name="ppt")
    timestamp = models.DateTimeField(auto_now_add=True)


class CustomError(Exception): 
    def __init__(self,ErrorInfo): 
        super().__init__(self) #初始化父类 
        self.errorinfo=ErrorInfo 
    def __str__(self): 
        return self.errorinfo
