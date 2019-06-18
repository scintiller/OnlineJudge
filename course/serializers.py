import re

from django import forms

from options.options import SysOptions
from utils.api import UsernameSerializer, serializers   # 就是rest framework的serializers

from .models import Course, PowerPoint

# 读取表单部分，根据表单来设定域
class CreateOrEditCourseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=1024)
    charpter = serializers.CharField(max_length=32)
    section = serializers.CharField(max_length=32)
    content = serializers.CharField()
    on_class_problems = serializers.ListField(child=serializers.CharField(max_length=32), allow_empty=False)
    after_class_problems = serializers.ListField(child=serializers.CharField(max_length=32), allow_empty=False)
    
class CreateCourseSerializer(CreateOrEditCourseSerializer):
    pass

class EditCourseSerializer(CreateOrEditCourseSerializer):
    id = serializers.IntegerField()

# 返回course页面的时候用到，根据模型来设定域
class BaseCourseSerializer(serializers.ModelSerializer):
    on_class_problems = serializers.SlugRelatedField(many=True, slug_field="_id", read_only=True)
    after_class_problems = serializers.SlugRelatedField(many=True, slug_field="_id", read_only=True)
    created_by = UsernameSerializer()

class CourseAdminSerializer(BaseCourseSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class CourseSerializer(BaseCourseSerializer):
    class Meta:
        model = Course
        fields = "__all__"

# 返回PPT时的serializer
class PowerPointSerializer(serializers.ModelSerializer):
    class Meta():
        model = PowerPoint
        fields = "__all__" 

# 返回PPT名字的serializer
class PowerPointNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024)