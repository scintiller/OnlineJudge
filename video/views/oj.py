import json

from account.decorators import login_required

from utils.api import APIView
from ..models import ProblemSolution
from ..serializers import ProblemSolutionSerializer

class SolutionVideoAPI(APIView):
    # 普通用户获取题解
    @login_required
    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if not problem_id:
            return self.error("请求中需要问题id")
        # 得到该问题的题解
        result = ProblemSolution.objects.filter(problem=problem_id)
        if not result.exists():
            return self.error("题解不存在")
        # 数据序列化
        problem_solution = result[0]
        data = ProblemSolutionSerializer(problem_solution).data
        
        return self.success(data)
        
        
