from rest_framework.parsers import MultiPartParser, FormParser
import json

from ..serializers import ProblemSolutionSerializer
from ..api import MediaAPIView
from ..models import ProblemSolution

from utils.api import validate_serializer
from problem.models import Problem
from account.decorators import problem_permission_required, ensure_created_by


class ProblemSolutionAPI(MediaAPIView):
    parser_classes = (MultiPartParser, FormParser)
    
    # 添加问题的题解
    @problem_permission_required
    def post(self, request):
        # 视频题解
        video_solution = request.data.get("video", None)
        data = {}
        if video_solution is not None:
            data['video_solution'] = video_solution
        # 文字题解
        text_solution = request.data.get("text", None)
        if text_solution is not None:
            data["text_solution"] = text_solution
        # 关联问题
        problem_id = request.data.get("problem_id",None)
        if problem_id==None:
            return self.error("没有问题id")
        try:    
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return self.error("问题不存在")
        data["problem"] = problem
        
        # 存储到数据库中
        solution_video = ProblemSolution.objects.create(**data)
        # 返回success
        return self.success(ProblemSolutionSerializer(solution_video).data)

    # 删除题解
    @problem_permission_required
    def delete(self, request):
        # 从数据库中找题解
        body = json.loads(request.body.decode("utf-8"))
        if "id" not in body:
            return self.error("没有提供题解id")
        solution_id = body['id']
        try:
            probelm_solution = ProblemSolution.objects.get(id=solution_id)
        except ProblemSolution.DoesNotExist:
            return self.error("题解不存在")
        # 删除视频
        probelm_solution.delete()
        return self.success()