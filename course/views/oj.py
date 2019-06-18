from utils.api import APIView
from video.api import MediaAPIView

from ..models import Course, PowerPoint
from ..serializers import CourseSerializer, PowerPointSerializer, PowerPointNameSerializer

class CourseAPI(APIView):
    def get(self, request):
        # 课程详情页
        course_id = request.GET.get("id")
        if course_id:
            try:
                course = Course.objects.select_related("created_by")\
                    .get(id=course_id)
                return self.success(CourseSerializer(course).data)
            except Course.DoesNotExist:
                return self.error("课程不存在")
        
        # 课程列表
        limit = request.GET.get("limit")
        if not limit:
            return self.error("需要给出每页的课程数限制！")
        
        courses = Course.objects.select_related("created_by")
        data = self.paginate_data(request, courses, CourseSerializer)
        return self.success(data)

class PowerPointAPI(MediaAPIView):
    # 普通用户获取ppt
    def get(self, request):
        course_id = request.GET.get("course_id")

        if course_id:       # str[str.rfind("/")+1:]
            # 从数据库中找ppt
            try:
                ppt = PowerPoint.objects.filter(course=course_id)[0]
                url = PowerPointSerializer(ppt).data['ppt']
                ppt_name = {"name": url[url.rfind("/")+1:]} 
                return self.success(PowerPointNameSerializer(ppt_name).data)
            except PowerPoint.DoesNotExist:
                return self.error("视频不存在")
        else:
            return self.error("请求中需要参数course_id")
