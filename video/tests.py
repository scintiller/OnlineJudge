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
    
    # 测试题解上传
    def test_upload_problem_solution(self):
        # 新建题目
        admin = self.create_admin()
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        #　请求数据
        self.data = {'video': self.created_file, 'text': "Test Test", 'problem_id': self.problem.id}
        # print("题解上传. url: ", self.url, "  data: ", self.data)
        resp = self.client.post(self.url, self.data, format="multipart")
        self.assertSuccess(resp)
        return resp
    
    # 测试没有填视频题解，也能上传成功
    def test_upload_solution_without_video(self):
        # 新建题目
        admin = self.create_admin()
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        # 测试没有填视频
        data = {'problem_id': self.problem.id}
        # print("可以不填视频, data：", data)
        resp = self.client.post(self.url, data, format="multipart")
        self.assertSuccess(resp)

    # 测试题解上传失败
    def test_upload_solution_without_problem(self):
        # 测试没有填题号
        data = {'video': self.created_file}
        resp = self.client.post(self.url, data, format="multipart")
        # print("resp.data: ", resp.data)
        self.assertFailed(resp)
    
    # 测试重复上传
    def test_upload_solution_twice(self):
        self.test_upload_problem_solution()
        resp = self.client.post(self.url, self.data, format="multipart")
        # print(resp.data)
        self.assertFailed(resp)

    # 测试题解删除
    def test_delete_solution(self):
        # 上传题解
        resp = self.test_upload_problem_solution()
        # 删除题解
        data = {"problem_id": resp.data['data']['problem']}  
        # print("删除题解，url: ", self.url, " data: ", data)
        resp = self.client.delete(self.url, data)
        self.assertSuccess(resp)
    
    # 测试删除不存在的题解
    def test_delete_unexisted_solution(self):
        data = {"problem_id": 100}  
        # print("删除题解，url: ", self.url, " data: ", data)
        resp = self.client.delete(self.url, data)
        # print("resp.data: ", resp.data)
        self.assertFailed(resp)

# 普通用户获取题解的测试
class SolutionVideoAPITest(SolutionVideoTestBase):
    def setUp(self):
        self.url = self.reverse("problem_solution_api")
        self.upload_url = self.reverse("problem_solution_admin_api")

    def test_get_solution(self):
        # 新建题目
        admin = self.create_admin(login=False)
        problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        # 生成文件
        self.super_admin = self.create_super_admin()
        created_file = self.create_test_file('/tmp/test_upload')
        # 新建题解
        self.data = {'video': created_file, 'problem_id': problem.id, 'text': "test solution"}
        resp = self.client.post(self.upload_url, self.data, format="multipart")
        self.video_data = resp.data['data']
        # 创建普通用户
        self.create_user("test", "test123")
        # 测试
        resp = self.client.get(self.url + "?problem_id="+ str(self.video_data["problem"])) 
        # print("普通用户访问url:", self.url + "?problem_id="+ str(self.video_data["problem"]))
        # print("普通用户访问的返回resp.data: ", resp.data)
        self.assertSuccess(resp)
    
    # 测试获取没有填视频的题解
    def test_get_solution_without_video(self):
        # 新建题目
        admin = self.create_admin(login=False)
        problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, admin)
        # 新建题解
        self.super_admin = self.create_super_admin()
        self.data = {'problem_id': problem.id, 'text': "test solution"}
        resp = self.client.post(self.upload_url, self.data, format="multipart")
        # 创建普通用户
        self.create_user("test", "test123")
        # 测试
        resp = self.client.get(self.url + "?problem_id="+ str(problem.id)) 
        # print("resp.data: ", resp.data)
        self.assertSuccess(resp)

    # 测试题解不存在
    def test_get_nonexisted_solution(self):
        resp = self.client.get(self.url + "?problem_id="+ str(100)) 
        # print("resp.data: ", resp.data)
        self.assertFailed(resp)