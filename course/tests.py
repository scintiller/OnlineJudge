import copy
import hashlib
import os
import shutil

from utils.api.tests import APITestCase

from .models import Course
from .views.admin import CourseAPI

from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase

DEFAULT_COURSE_DATA = {"display_id": "A-1", "title": "test course", 
                        "content": "<p>test course</p>", "on_class_problems": ["A-110"],
                        "after_class_problems": ["A-110"],} 
                        #  


class CourseAdminAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("course_admin_api")
        super_admin = self.create_super_admin()
        ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, super_admin)
        self.data = copy.deepcopy(DEFAULT_COURSE_DATA)
    
    def test_create_course(self):
        # 正常添加课程
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        return resp
    
    def test_create_course_failure(self):
        # 课堂练习题目不存在时添加课程失败
        test_data = self.data
        test_data["on_class_problems"] = ["problem_not_exist"]
        resp = self.client.post(self.url, data=test_data)
        self.assertFailed(resp)
        # 课后题目不存在时添加课程失败
        test_data = self.data
        test_data["after_class_problems"] = ["problem_not_exist"]
        resp = self.client.post(self.url, data=test_data)
        self.assertFailed(resp)

    def test_get_course(self):
        self.test_create_course()
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
    
    def test_get_one_course(self):
        course_id = self.test_create_course().data["data"]["id"]
        resp = self.client.get(self.url + "?id=" + str(course_id))
        self.assertSuccess(resp)
    
    def test_edit_course(self):
        course_id = self.test_create_course().data["data"]["id"]
        data = copy.deepcopy(self.data)
        data["id"] = course_id
        resp = self.client.put(self.url, data = data)
        self.assertSuccess(resp)

class CourseCreateTestBase(APITestCase):
    @staticmethod
    def add_course(course_data, created_by):
        data = copy.deepcopy(course_data)
        data["created_by"] = created_by
        ProblemCreateTestBase
        tmp = CourseAPI()
        course = tmp.create_course(data)

        return course

class CourseAPITest(CourseCreateTestBase):
    def setUp(self):
        self.url = self.reverse("course_api")
        # 新建题目
        super_admin = self.create_super_admin()
        ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, super_admin)
        # 新建课程
        admin = self.create_admin(login=False)
        self.course = self.add_course(DEFAULT_COURSE_DATA, admin)
        self.create_user("test", "test123")

    def test_get_course_list(self):
        resp = self.client.get(f"{self.url}?limit=10")
        self.assertSuccess(resp)

    def test_get_one_course(self):
        resp = self.client.get(self.url + "?course_id=" + str(self.course.display_id))
        self.assertSuccess(resp)
