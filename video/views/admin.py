from rest_framework.parsers import MultiPartParser, FormParser
import json

from ..serializers import SolutionVideoSerializer
from ..api import MediaAPIView
from ..models import SolutionVideo

from utils.api import validate_serializer
from problem.models import Problem
from account.decorators import problem_permission_required, ensure_created_by


class SolutionVideoAPI(MediaAPIView):
    parser_classes = (MultiPartParser, FormParser)
    
    # 添加问题的视频
    @problem_permission_required
    def post(self, request):
        # 从request里取出video数据
        video = request.data.get("video", None)
        if video==None:
            return self.error("没有上传视频")
        data = {'video': video}
        # 关联问题
        problem_id = request.data.get("problem_id",None)
        if problem_id==None:
            return self.error("没有问题id")
        try:    
            problem = Problem.objects.get(id=problem_id)
            #ensure_created_by(problem, video_data["current_user"])
        except Problem.DoesNotExist:
            return self.error("问题不存在")
        data["problem"] = problem
        # 存储到数据库中
        solution_video = SolutionVideo.objects.create(**data)
        # 返回success
        return self.success(SolutionVideoSerializer(solution_video).data)

    # 删除一个视频（根据video_id）
    @problem_permission_required
    def delete(self, request):
        # 从数据库中找视频
        body = json.loads(request.body.decode("utf-8"))
        if "video_id" not in body:
            return self.error("没有视频id")
        video_id = body['video_id']
        try:
            video = SolutionVideo.objects.get(id=video_id)
        except SolutionVideo.DoesNotExist:
            return self.error("视频不存在")
        # 删除视频
        video.delete()
        return self.success()
