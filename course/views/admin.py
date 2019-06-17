from rest_framework.parsers import MultiPartParser, FormParser
import json

from utils.api import APIView, validate_serializer
from video.api import MediaAPIView

from problem.models import Problem

from ..models import Course, PowerPoint
from ..serializers import (CreateCourseSerializer, EditCourseSerializer, 
                           CourseAdminSerializer, CourseSerializer, PowerPointSerializer)
from account.decorators import problem_permission_required, ensure_created_by

class CourseAPI(APIView):
#    @course_permission_requred
    @validate_serializer(CreateCourseSerializer)
    # 创建一节新的课
    def post(self, request):
        data = request.data
        # 验证ID号在数据库中合法
        display_id = data["display_id"]
        if not display_id:
            return self.error("需要填写课程ID号")
        if Course.objects.filter(display_id=display_id).exists():
            return self.error("所填课程ID号已存在")
        # 课程创建者
        data["created_by"] = request.user
        # 创建课程，并添加课程练习和课后作业
        course = self.create_course(data)
        if course == None:
            return self.error("添加的课程不存在")
        return self.success(CourseAdminSerializer(course).data)
    
#    @course_permission_required
    def get(self, request):
        course_id = request.GET.get("id")
        user = request.user
        # 编辑这节课的页面
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                ensure_created_by(course, user)
                return self.success(CourseAdminSerializer(course).data)
            except Course.DoesNotExist:
                return self.error("课程不存在")
        # 课程列表页面
        # 从数据库取出所有课程
        courses = Course.objects.order_by("-create_time")
        # 根据权限筛选
#        if not user.can_mgmt_all_course():
#            courses = courses.filter(created_by=user)
        return self.success(self.paginate_data(request, courses, CourseAdminSerializer))

#    @course_permission_required
    @validate_serializer(EditCourseSerializer)
    # 重新编辑好以后，更新这节课
    def put(self, request):
        data = request.data
        course_id = data.pop("id")

        try:
            course = Course.objects.get(id=course_id)
            ensure_created_by(course, request.user)
        except Problem.DoesNotExist:
            return self.error("课程不存在")

        on_class_problems = data.pop("on_class_problems")
        after_class_problems = data.pop("after_class_problems")

        # put操作，更新这节课的信息
        for k, v in data.items():
            setattr(course, k, v)
        course.save()

        # 更新课堂题目
        course.on_class_problems.remove(*course.on_class_problems.all())
        course = self.add_on_class_problems(course, on_class_problems)
        if course == None:
            return self.error("课堂练习题目不存在")
        # 更新课后习题
        course.after_class_problems.remove(*course.after_class_problems.all())
        course = self.add_after_class_problems(course, after_class_problems)
        if course == None:
            return self.error("课后题目不存在")

        return self.success()

#   @problem_permission_required
    def delete(self, request):
        course_id = request.GET.get("id")
        if not course_id:
            return self.error("缺少id号")
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return self.error("问题不存在")
        ensure_created_by(course, request.user)
        course.delete()
        return self.success()

    # 保存课堂题目
    def add_on_class_problems(self, course, problems):
        if course == None:
            return None
        for item in problems:
            try:
                problem = Problem.objects.get(_id=item)
            except Problem.DoesNotExist:
                return None
            course.on_class_problems.add(problem)
        return course

    # 保存课后题目
    def add_after_class_problems(self, course, problems):
        if course == None:
            return None
        for item in problems:
            try:
                problem = Problem.objects.get(_id=item)
            except Problem.DoesNotExist:
                return None
            course.after_class_problems.add(problem)
        return course

    # 在数据库中创建课程
    def create_course(self, data):
        # problems是多对多的，不能直接用create保存
        on_class_problems = data.pop("on_class_problems")
        after_class_problems = data.pop("after_class_problems")
        # 写入数据库
        course = Course.objects.create(**data)
        # 保存课堂题目
        course = self.add_on_class_problems(course, on_class_problems)
        #　保存课后习题
        course = self.add_after_class_problems(course, after_class_problems)
        return course

# PPT相关接口
class PowerPointAPI(MediaAPIView):
    parser_classes = (MultiPartParser, FormParser)
    
    # 添加课程的PPT
    @problem_permission_required
    def post(self, request):
        # 从request里取出ppt
        ppt = request.data.get("ppt", None)
        if ppt==None:
            return self.error("没有上传ppt")
        data = {'ppt': ppt}
        # 关联问题
        course_id = request.data.get("course_id",None)
        if course_id==None:
            return self.error("没有课程id")
        try:    
            course = Course.objects.get(id=course_id)
        except Problem.DoesNotExist:
            return self.error("课程不存在")
        data["course"] = course
        # 存储到数据库中
        powerpoint = PowerPoint.objects.create(**data)
        # 返回success
        return self.success(PowerPointSerializer(powerpoint).data)

    # 删除一个ppt（根据ppt_id）
    @problem_permission_required
    def delete(self, request):
        # 从数据库中找ppt
        ppt_id = request.GET.get("id")
        if not ppt_id:
            return self.error("缺少id号")
        try:
            ppt = PowerPoint.objects.get(id=ppt_id)
        except PowerPoint.DoesNotExist:
            return self.error("ppt不存在")
        # 删除ppt
        ppt.delete()
        return self.success()
