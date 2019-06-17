import json

from ..api import MediaAPIView
from ..models import SolutionVideo
from ..serializers import SolutionVideoSerializer

class SolutionVideoAPI(MediaAPIView):
    # 普通用户获取视频
    def get(self, request):
        video_id = request.GET.get("video_id")

        if video_id:
            # 从数据库中找视频
            try:
                video = SolutionVideo.objects.get(id=video_id)
                return self.success(SolutionVideoSerializer(video).data)
            except SolutionVideo.DoesNotExist:
                return self.error("视频不存在")
        else:
            return self.error("请求中需要参数video_id")

        
        
