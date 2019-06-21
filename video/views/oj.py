import json

from account.decorators import login_required

from ..api import MediaAPIView
from ..models import ProblemSolution
from ..serializers import ProblemSolutionSerializer

class SolutionVideoAPI(MediaAPIView):
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
        url = data.pop("video")
        if url is not None:
            data["file_name"] = url[url.rfind("/")+1:]
            data["file_type"] = "video"
        else:
            data["file_name"] = None
            data["file_type"] = None
        
        return self.success(data)
        
        
