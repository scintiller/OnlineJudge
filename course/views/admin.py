from rest_framework.parsers import MultiPartParser, FormParser
import json

from utils.api import APIView, validate_serializer
from video.api import MediaAPIView

from problem.models import Problem

from ..models import Course, PowerPoint, CustomError
from ..serializers import (CreateCourseSerializer, EditCourseSerializer, 
                           CourseAdminSerializer, CourseSerializer, PowerPointSerializer)
from account.decorators import super_admin_required, ensure_created_by

class CourseAPI(APIView):
    @super_admin_required
    @validate_serializer(CreateCourseSerializer)
    # 创建一节新的课
    def post(self, request):
        data = request.data
        # 验证ID号在数据库中合法
        charpter = data["charpter"]
        section = data['section']
        if Course.objects.filter(charpter=charpter, section=section).exists():
            return self.error("所填课程的章节和序号已存在")
        # 课程创建者
        data["created_by"] = request.user
        # 创建课程，并添加课程练习和课后作业
        try:
            course = self.create_course(data)
        except CustomError as e:
            return self.error(e.errorinfo)
        return self.success(CourseAdminSerializer(course).data)
    
    @super_admin_required
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

    @super_admin_required
    @validate_serializer(EditCourseSerializer)
    # 重新编辑好以后，更新这节课
    def put(self, request):
        data = request.data
        course_id = data.pop("id")

        # 查询课程存不存在
        try:
            course = Course.objects.get(id=course_id)
            ensure_created_by(course, request.user)
        except Problem.DoesNotExist:
            return self.error("课程不存在")

        # 查询problems存不存在
        try:
            data, on_class_problems, after_class_problems = self.get_problems(data)
        except CustomError as e:
            raise e

        # put操作，更新这节课的信息
        for k, v in data.items():
            setattr(course, k, v)
        course.save()

        # 更新课堂题目
        course.on_class_problems.remove(*course.on_class_problems.all())
        for problem in on_class_problems:
            course.on_class_problems.add(problem)
        # 更新课后习题
        course.after_class_problems.remove(*course.after_class_problems.all())
        for problem in after_class_problems:
            course.after_class_problems.add(problem)

        return self.success()

    @super_admin_required
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
    def get_on_class_problems(self, data):
        problems = data.pop("on_class_problems")
        on_class_problems = []
        for item in problems:
            try:
                problem = Problem.objects.get(_id=item)
                on_class_problems.append(problem) 
            except Problem.DoesNotExist:
                raise CustomError("课堂题目不存在")

        return data, on_class_problems

    # 保存课后题目
    def get_after_class_problems(self, data):
        problems = data.pop("after_class_problems")
        after_class_problems = []
        for item in problems:
            try:
                problem = Problem.objects.get(_id=item)
                after_class_problems.append(problem)
            except Problem.DoesNotExist:
                raise CustomError("课后作业题目不存在")
            
        return data, after_class_problems
    
    def get_problems(self, data):
        # 查找on_class_problems
        try:
            data, on_class_problems = self.get_on_class_problems(data)
        except CustomError as e:
            raise e
        # 查找after_class_problems
        try: 
            data, after_class_problems = self.get_after_class_problems(data)
        except CustomError as e:
            raise e
        
        return data, on_class_problems, after_class_problems

    # 在数据库中创建课程
    def create_course(self, data):
        try:
            data, on_class_problems, after_class_problems = self.get_problems(data)
        except CustomError as e:
            raise e
        # 写入数据库
        course = Course.objects.create(**data)
        if course == None:
            raise CustomError("课程创建失败")
        # 保存题目
        for problem in on_class_problems:
            course.on_class_problems.add(problem)
        for problem in after_class_problems:
            course.after_class_problems.add(problem)
        return course

# PPT相关接口
class PowerPointAPI(MediaAPIView):
    parser_classes = (MultiPartParser, FormParser)
    
    # 添加课程的PPT
    @super_admin_required
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

    # 删除一个ppt（根据course_id）
    @super_admin_required
    def delete(self, request):
        # 从数据库中找ppt
        course_id = request.GET.get("course_id")
        if not course_id:
            return self.error("缺少course_id号")
        try:
            ppt = PowerPoint.objects.filter(course=course_id)[0]
        except PowerPoint.DoesNotExist:
            return self.error("ppt不存在")
        # 删除ppt
        ppt.delete()
        return self.success()
