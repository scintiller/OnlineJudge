import json

from ..api import MediaAPIView
from ..models import ProblemSolution
from ..serializers import ProblemSolutionSerializer

class SolutionVideoAPI(MediaAPIView):
    # 普通用户获取视频
    def get(self, request):
        video_id = request.GET.get("problem_id")

        if video_id:
            # 从数据库中找视频
            try:
                video = ProblemSolution.objects.get(id=video_id)
                return self.success(ProblemSolutionSerializer(video).data)
            except ProblemSolution.DoesNotExist:
                return self.error("题解不存在")
        else:
            return self.error("请求中需要题解id")
            
        
