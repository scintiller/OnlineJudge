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
        data = {}
        # 判断该问题是否已经有题解
        problem_id = request.data.get("problem_id",None)
        if problem_id==None:
            return self.error("没有参数problem_id")
        try:    
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return self.error("问题不存在")
        try:
            ProblemSolution.objects.get(problem=problem_id)
        except ProblemSolution.DoesNotExist:    # 题解不存在，该题还没有题解, 关联问题
            data["problem"] = problem
        else:                                   # 题解存在，该题已经有题解
            return self.error("该问题已经有题解了！")

        # 视频题解
        video = request.data.get("video", None)
        if video is not None:
            data['video'] = video
        # 文字题解
        text = request.data.get("text", None)
        if text is not None:
            data["text"] = text
        
        # 存储到数据库中
        solution_video = ProblemSolution.objects.create(**data)
        # 返回success
        return self.success(ProblemSolutionSerializer(solution_video).data)

    # 删除题解
    @problem_permission_required
    def delete(self, request):
        # 从数据库中找题解
        body = json.loads(request.body.decode("utf-8"))
        if "problem_id" not in body:
            return self.error("没有提供problem_id")
        problem_id = body['problem_id']
        try:
            probelm_solution = ProblemSolution.objects.get(problem=problem_id)
        except ProblemSolution.DoesNotExist:
            return self.error("题解不存在")
        # 删除视频
        probelm_solution.delete()
        return self.success()
