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
        print("[DEBUG]***start*** solution problem_id: ", problem_id)
        if problem_id:
            # 从数据库中找题解
            try:
                problem_solution = ProblemSolution.objects.get(problem=problem_id)
            except ProblemSolution.DoesNotExist:
                return self.error("题解不存在")
        else:
            return self.error("请求中需要问题id")
        
        data = ProblemSolutionSerializer(problem_solution).data
        print("[DEBUG] solution data: ", data)
        url = data.pop("video")
        print("[DEBUG] solution url: ", url)
        if url is not None:
            data["file_name"] = url[url.rfind("/")+1:]
            data["file_type"] = "video"
            print("[DEBUG] solution file_name: ", data["file_name"])
            print("[DEBUG] solution file_type: ", data["file_type"])
        else:
            data["file_name"] = None
            data["file_type"] = None
        
        return self.success(data)
        
        
