from rest_framework.views import APIView
import json
from django.http import HttpResponse

class JSONResponse(object):
    content_type = "application/json;charset=UTF-8"

    @classmethod
    def response(cls, data):
        resp = HttpResponse(json.dumps(data, indent=4), content_type=cls.content_type)
        resp.data = data
        return resp

# 因为原先的APIView没法处理视频上传所需的[MultiPartParser, FormParser]，自己新定义了一个VideoAPIView类，输入输出接口与其他的View中的APIView类相同
class MediaAPIView(APIView):
    response_class = JSONResponse
    
    def response(self, data):
        return self.response_class.response(data)

    def success(self, data=None):
        return self.response({"error": None, "data": data})

    def error(self, msg="error", err="error"):
        return self.response({"error": err, "data": msg})
