import os
import logging
from django.conf import settings
from django.http import FileResponse

from utils.api import CSRFExemptAPIView, APIView
from video.api import MediaAPIView
from account.serializers import ImageUploadForm, FileUploadForm
from account.decorators import login_required
from utils.shortcuts import rand_str

from ..models import Course, PowerPoint
from ..serializers import CourseSerializer, PowerPointSerializer, FileDownloadSerializer


logger = logging.getLogger(__name__)

class CourseAPI(APIView):
    @login_required
    def get(self, request):
        # 判断user权限
        user = request.user
        if not user.is_super_admin() and not user.is_admin_role() and not user.paid:
            return self.error("没有查看课程权限")
            
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
    @login_required
    def get(self, request):
        course_id = request.GET.get("course_id")

        if course_id:       # str[str.rfind("/")+1:]
            # 从数据库中找ppt
            try:
                ppt = PowerPoint.objects.filter(course=course_id)[0]
                url = PowerPointSerializer(ppt).data['ppt']
                ppt_name = {"file_type": "ppt", "file_name": url[url.rfind("/")+1:]} 
                return self.success(FileDownloadSerializer(ppt_name).data)
            except PowerPoint.DoesNotExist:
                return self.error("ppt不存在")
        else:
            return self.error("请求中需要参数course_id")

###########################   File Download / File Upload  ###########################

class FileDownloadAPI(APIView):
    @login_required
    def get(self, request):
        file_type = request.GET.get("file_type").lower()
        if self.check_file_type(file_type) == False:
            return self.error("该文件类型不存在："+ file_type + ", file_type参数只接受ppt/image/video/file")
        file_name = request.GET.get("file_name").lower()
        file_address = os.path.join(settings.MEDIA_ROOT, file_type, file_name)
        # print("file address: ", file_address)
        try: 
            open_file = open(file_address,'rb')
        except IOError: 
            return self.error("文件不存在")
        response = FileResponse(open_file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
        # print("response:", response)
        return response
        
    def check_file_type(self, file_type):
        if file_type == "ppt" or file_type == "image" or file_type == "video" or file_type == "file":
            return True
        return False

# 上传图片
class ImageUploadAPIView(CSRFExemptAPIView):
    request_parsers = ()

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data["image"]
        else:
            return self.response({
                "success": False,
                "msg": "Upload failed"
                })

        suffix = os.path.splitext(img.name)[-1].lower()
        if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.response({
                "success": False,
                "msg": "Unsupported file format"
                })
        img_name = rand_str(10) + suffix
        file_address = os.path.join(settings.MEDIA_ROOT, "image", img_name)
        # print("file_address: ", file_address)
        try:
            with open(file_address, "wb") as imgFile:
                for chunk in img:
                    imgFile.write(chunk)
        except IOError as e:
            logger.error(e)
            return self.response({
                "success": False,
                "msg": "Upload Error"
                })
        return self.response({
            "success": True,
            "msg": "Success"
            })

# 上传文件
class FileUploadAPIView(CSRFExemptAPIView):
    request_parsers = ()

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
        else:
            return self.response({
                "success": False,
                "msg": "Upload failed"
            })

        suffix = os.path.splitext(file.name)[-1].lower()
        file_name = rand_str(10) + suffix
        file_address = os.path.join(settings.MEDIA_ROOT, "file", file_name)
        try:
            with open(file_address, "wb") as f:
                for chunk in file:
                    f.write(chunk)
        except IOError as e:
            logger.error(e)
            return self.response({
                "success": False,
                "msg": "Upload Error"})
        return self.response({
            "success": True,
            "msg": "Success",
            })
        