import json

from account.decorators import login_required

from utils.api import APIView
from ..models import ProblemSolution
from ..serializers import ProblemSolutionSerializer

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkvod.request.v20170321 import GetVideoPlayAuthRequest

accessId = "LTAIiCguUbtEbEnB"
accessKeySecret = "6878WQdrA93To3zkchGIiRbavmXaLE"
regionId = "cn-shanghai"


class SolutionVideoAPI(APIView):

    def __getPlayAuth(self, vid):
        connectTimeout = 3
        client = AcsClient(accessId, accessKeySecret, regionId, auto_retry=True, max_retry_time=3, timeout=connectTimeout)
        request = GetVideoPlayAuthRequest.GetVideoPlayAuthRequest()
        request.set_accept_format('JSON')
        request.set_VideoId(vid)
        request.set_AuthInfoTimeout(3600 * 5)
        try:
            response = json.loads(client.do_action_with_exception(request))
        except Exception as e:
            return ""
        playauth = response.get("PlayAuth")
        return playauth


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
        video_id = problem_solution.video

        data = ProblemSolutionSerializer(problem_solution).data
        data["playauth"] = self.__getPlayAuth(video_id)
        return self.success(data)
        

