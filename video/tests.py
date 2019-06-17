import copy

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from utils.api.tests import APITestCase
from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase

from .views.admin import ProblemSolutionAPI

class SolutionVideoTestBase(APITestCase):
    # 生成文件
    def create_test_file(self, path):
        f = open(path, 'w')
        f.write('test123\n')
        f.close()
        f = open(path, 'rb')
        return f

        
# admin上传删除视频的测试
class ProblemSolutionAdminAPITest(SolutionVideoTestBase):
    def setUp(self):
        self.url = self.reverse("problem_solution_admin_api")
        # 生成文件
        self.super_admin = self.create_super_admin()
        self.created_file = self.create_test_file('/tmp/test_upload')
        # 新建题目
        admin = self.create_admin()
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
    
    # 测试题解上传
    def test_upload_problem_solution(self):
        data = {'video': self.created_file, 'text': "Test Test", 'problem_id': self.problem.id}
        # print("题解上传. url: ", self.url, "  data: ", data)
        resp = self.client.post(self.url, data, format="multipart")
        self.assertSuccess(resp)
        return resp
    
    # 测试没有填视频题解，也能上传成功
    def test_upload_solution_without_video(self):
        # 测试没有填视频
        data = {'problem_id': self.problem.id}
        # print("可以不填视频, data：", data)
        resp = self.client.post(self.url, data, format="multipart")
        self.assertSuccess(resp)

    # 测试题解上传失败
    def test_upload_solution_video_with_problem(self):
        # 测试没有填题号
        data = {'video': self.created_file}
        resp = self.client.post(self.url, data, format="multipart")
        self.assertFailed(resp)

    # 测试题解删除
    def test_delete_solution_video(self):
        # 上传题解
        resp = self.test_upload_problem_solution()
        # 删除题解
        data = {"id": resp.data['data']['id']}  
        # print("删除题解，url: ", self.url, " data: ", data)
        resp = self.client.delete(self.url, data)
        self.assertSuccess(resp)

# 普通用户获取题解的测试
class SolutionVideoAPITest(SolutionVideoTestBase):
    def setUp(self):
        self.url = self.reverse("problem_solution_api")
        self.upload_url = self.reverse("problem_solution_admin_api")
        # 新建题目
        admin = self.create_admin(login=False)
        problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        # 生成文件
        self.super_admin = self.create_super_admin()
        created_file = self.create_test_file('/tmp/test_upload')
        # 新建题解
        self.data = {'video': created_file, 'problem_id': problem.id}
        resp = self.client.post(self.upload_url, self.data, format="multipart")
        self.video_data = resp.data['data']
        # 创建普通用户
        self.create_user("test", "test123")

    def test_get_video(self):
        resp = self.client.get(self.url + "?id="+ str(self.video_data["id"])) 
        # print("普通用户访问url:", self.url + "?id="+ str(self.video_data["id"]))
        print("普通用户访问的返回resp.data: ", resp.data)
        self.assertSuccess(resp)