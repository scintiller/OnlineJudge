import json

from ..api import MediaAPIView
from ..models import ProblemSolution
from ..serializers import ProblemSolutionSerializer

class SolutionVideoAPI(MediaAPIView):
    # 普通用户获取题解
    def get(self, request):
        problem_id = request.GET.get("problem_id")

        if problem_id:
            # 从数据库中找题解
            try:
                problem_solution = ProblemSolution.objects.get(problem=problem_id)
            except ProblemSolution.DoesNotExist:
                return self.error("题解不存在")
        else:
            return self.error("请求中需要问题id")
        
        data = ProblemSolutionSerializer(problem_solution).data
        url = data.pop("video")
        data["file_name"] = url[url.rfind("/")+1:]
        data["file_type"] = "video"
        
        return self.success(data)
        
        
