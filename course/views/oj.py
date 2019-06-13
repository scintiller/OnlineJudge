from utils.api import APIView
from ..models import Course
from ..serializers import CourseSerializer

class CourseAPI(APIView):
    def get(self, request):
        # 课程详情页
        course_id = request.GET.get("course_id")
        if course_id:
            try:
                course = Course.objects.select_related("created_by")\
                    .get(display_id=course_id)
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
    