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

# 测试课程admin接口
class CourseAdminAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("course_admin_api")
        super_admin = self.create_super_admin()
        ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, super_admin)
        self.data = copy.deepcopy(DEFAULT_COURSE_DATA)
    
    def test_create_course(self):
        # 正常添加课程
        #print("admin 添加课程. 方法：post / url:", self.url, " / data: ", self.data)
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
        # print("data: ", data)
        resp = self.client.put(self.url, data = data)
        self.assertSuccess(resp)
    
    def test_delete_course(self):
        course_id = self.test_create_course().data["data"]["id"]
        # print("course id url = ", self.url + "?id=" + str(course_id))
        resp = self.client.delete(self.url + "?id=" + str(course_id))
        self.assertSuccess(resp)

class CourseCreateTestBase(APITestCase):
    @staticmethod
    def add_course(course_data, created_by):
        data = copy.deepcopy(course_data)
        data["created_by"] = created_by
        tmp = CourseAPI()
        course = tmp.create_course(data)

        return course

# 测试课程普通用户接口
class CourseAPITest(CourseCreateTestBase):
    def setUp(self):
        self.url = self.reverse("course_api")
        # 新建题目
        super_admin = self.create_super_admin()
        ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, super_admin)
        # 新建课程
        admin = self.create_admin(login=False)
        self.course = self.add_course(DEFAULT_COURSE_DATA, admin)
        # 新建普通用户
        self.create_user("test", "test123")

    def test_get_course_list(self):
        resp = self.client.get(f"{self.url}?limit=10")
        # print("course list get url: ", f"{self.url}?limit=10")
        self.assertSuccess(resp)

    def test_get_one_course(self):
        resp = self.client.get(self.url + "?id=" + str(self.course.id))
        # print("get one course url: ", self.url + "?id=" + str(self.course.id))
        self.assertSuccess(resp)

# 测试ppt admin接口
class PowerPointTestBase(APITestCase):
    # 生成文件
    def create_test_file(self, path):
        f = open(path, 'w')
        f.write('test123\n')
        f.close()
        f = open(path, 'rb')
        return f
        
# admin ppt上传删除的测试
class PowerPointAdminAPITest(PowerPointTestBase, CourseCreateTestBase):
    def setUp(self):
        self.url = self.reverse("ppt_admin_api")
        # 生成文件
        self.super_admin = self.create_super_admin()
        self.created_file = self.create_test_file('/tmp/test_upload')
        # 新建题目
        admin = self.create_admin()
        ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        # 新建课程
        self.course = self.add_course(DEFAULT_COURSE_DATA, admin)
    
    # 测试ppt上传
    def test_upload_ppt(self):
        # 发送post测试ppt上传
        data = {'ppt': self.created_file, 'course_id': self.course.id}
        # print("admin ppt upload. url: ", self.url, " / data: ", data)
        resp = self.client.post(self.url, data, format="multipart")
        print("ppt information: ", resp.data)
        self.assertSuccess(resp)
        return resp

    # 测试ppt删除
    def test_delete_solution_video(self):
        # 上传ppt
        resp = self.test_upload_ppt()
        # 删除视频
        ppt_id = resp.data['data']['id']
        # print("delete ppt url: ", self.url+ "?id=" + str(ppt_id))
        resp = self.client.delete(self.url+ "?id=" + str(ppt_id))
        self.assertSuccess(resp) 

# 普通用户测试获取ppt
class PowerPointAPITest(PowerPointTestBase, CourseCreateTestBase):
    def setUp(self):
        self.url = self.reverse("ppt_api")
        self.upload_url = self.reverse("ppt_admin_api")
        # 生成文件
        self.super_admin = self.create_super_admin()
        self.created_file = self.create_test_file('/tmp/test_upload')
        # 新建题目
        admin = self.create_admin()
        ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        # 新建课程
        self.course = self.add_course(DEFAULT_COURSE_DATA, admin)
        # 新建ppt
        data = {'ppt': self.created_file, 'course_id': self.course.id}
        resp = self.client.post(self.upload_url, data, format="multipart")
        self.ppt_data = resp.data['data']
        # 创建普通用户
        self.create_user("test", "test123")

    def test_get_ppt(self):
        # print("get ppt url: ", self.url + "?ppt_id="+ str(self.ppt_data["id"]))
        resp = self.client.get(self.url + "?ppt_id="+ str(self.ppt_data["id"])) # 
        self.assertSuccess(resp)    

    