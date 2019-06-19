import os
import re
import xlsxwriter

from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password

from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.shortcuts import rand_str

from ..decorators import super_admin_required
from ..models import AdminType, ProblemPermission, User, UserProfile, Class
from ..serializers import EditUserSerializer, UserAdminSerializer, GenerateUserSerializer, UsernameSerializer, ClassSerializer
from ..serializers import ImportUserSeralizer

from utils.cache import cache
import hashlib
import time


class CodeAdminAPI(APIView):
    @super_admin_required
    def get(self, request):
        expire_day = request.GET.get("expire_day")
        if not expire_day:
            expire_day = 7
        time_stamp = int(time.time())
        SALT = "闷声发大财"
        hl = hashlib.md5()
        str = SALT + time_stamp
        hl.update(str.encode("utf8"))
        code = hl.hexdigest()

        # store into redis
        cache.set(code, 'ALL', expire_day*24*3600)
        data = {"code": code}
        self.success(data)


class ClassAPI(APIView):
    def get(self, request):
        username = request.GET.get("username")
        teacher = request.user
        try:
            if username:
                teacher = User.objects.get(username=username, is_disabled=False)
        except User.DoesNotExist:
            return self.error("User does not exist")

        classes = teacher.class_set.all()
        class_array = []
        for c in classes:
            class_array.append(ClassSerializer(c).data)

        result = {
            "user_name": username,
            "classes": []
        }
        self.success(result)


class SetClassAPI(APIView):
    def get(self, request):
        class_name = request.GET("class_name")
        user_name = request.GET("user_name")
        if class_name:
            try:
                c = Class.objects.get(class_name=class_name)
            except Class.DoesNotExist:
                return self.error("Class does not exist")
        else:
            return self.error("class name not exist")
        if user_name:
            try:
                student = User.objects.get(username=class_name)
            except User.DoesNotExist:
                return self.error("Student does not exist")
        else:
            return self.error("user name not exist")

        student.in_class = c
        student.save()

        return self.success()


class ClassStudentAPI(APIView):
    def get(self, request):
        class_name = request.GET("class_name")
        if class_name:
            try:
                c = Class.objects.get(class_name=class_name)
            except Class.DoesNotExist:
                return self.error("Class does not exist")
            students = c.user_set.all()
        else:
            self.error("class name not exist")
        data = {}
        data["results"] = UsernameSerializer(students, many=True).data
        return self.success(data)


class ClassAdminAPI(APIView):
    @super_admin_required
    def post(self, request):
        name = request.data["class_name"]
        if not name:
            self.error("class name does not exist")
        teacher_name = request.data["teacher_name"]
        # query teacher
        if teacher_name:
            try:
                teacher = User.objects.get(username=teacher_name, is_disabled=False)
            except User.DoesNotExist:
                return self.error("Teacher does not exist")
        else:
            return self.error("teacher name does not exist")

        c = Class(class_name=name, teacher=teacher)
        c.save()
        return self.success()

    @super_admin_required
    def put(self, request):
        data = request.data
        try:
            c = Class.objects.get(id=data["id"])
        except Class.DoesNotExist:
            self.error("class does not exist")

        if data["class_name"]:
            # check class name
            if Class.objects.filter(class_name=data["class_name"]).exclude(id=c.id).exists():
                return self.error("class name already exists")

            c.class_name = data["class_name"]
            c.save()

        if data["teacher_name"]:
            teacher_name = request.data["teacher_name"]
            try:
                teacher = User.objects.get(username=teacher_name, is_disabled=False)
            except User.DoesNotExist:
                return self.error("Teacher does not exist")
            c.teacher = teacher
            c.save()

        return self.success()

    @super_admin_required
    def delete(self, request):
        id = request.GET.get("id")
        if not id:
            self.error("class id does not exist")
        try:
            c = Class.objects.get(id=id)
        except Class.DoesNotExist:
            return self.error("Class does not exist")
        c.delete()
        return self.success()


class UserAdminAPI(APIView):
    @validate_serializer(ImportUserSeralizer)
    @super_admin_required
    def post(self, request):
        """
        Import User
        """
        data = request.data["users"]

        user_list = []
        for user_data in data:
            if len(user_data) != 3 or len(user_data[0]) > 32:
                return self.error(f"Error occurred while processing data '{user_data}'")
            user_list.append(User(username=user_data[0], password=make_password(user_data[1]), email=user_data[2]))

        try:
            with transaction.atomic():
                ret = User.objects.bulk_create(user_list)
                UserProfile.objects.bulk_create([UserProfile(user=user) for user in ret])
            return self.success()
        except IntegrityError as e:
            # Extract detail from exception message
            #    duplicate key value violates unique constraint "user_username_key"
            #    DETAIL:  Key (username)=(root11) already exists.
            return self.error(str(e).split("\n")[1])

    @validate_serializer(EditUserSerializer)
    @super_admin_required
    def put(self, request):
        """
        Edit user api
        """
        data = request.data
        try:
            user = User.objects.get(id=data["id"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        if User.objects.filter(username=data["username"].lower()).exclude(id=user.id).exists():
            return self.error("Username already exists")
        if User.objects.filter(email=data["email"].lower()).exclude(id=user.id).exists():
            return self.error("Email already exists")

        pre_username = user.username
        user.username = data["username"].lower()
        user.email = data["email"].lower()
        user.admin_type = data["admin_type"]
        user.is_disabled = data["is_disabled"]

        if data["admin_type"] == AdminType.ADMIN:
            user.problem_permission = data["problem_permission"]
        elif data["admin_type"] == AdminType.SUPER_ADMIN:
            user.problem_permission = ProblemPermission.ALL
        else:
            user.problem_permission = ProblemPermission.NONE

        if data["password"]:
            user.set_password(data["password"])

        if data["open_api"]:
            # Avoid reset user appkey after saving changes
            if not user.open_api:
                user.open_api_appkey = rand_str()
        else:
            user.open_api_appkey = None
        user.open_api = data["open_api"]

        if data["two_factor_auth"]:
            # Avoid reset user tfa_token after saving changes
            if not user.two_factor_auth:
                user.tfa_token = rand_str()
        else:
            user.tfa_token = None

        user.two_factor_auth = data["two_factor_auth"]

        user.save()
        if pre_username != user.username:
            Submission.objects.filter(username=pre_username).update(username=user.username)

        UserProfile.objects.filter(user=user).update(real_name=data["real_name"])
        return self.success(UserAdminSerializer(user).data)

    @super_admin_required
    def get(self, request):
        """
        User list api / Get user by id
        """
        user_id = request.GET.get("id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self.error("User does not exist")
            return self.success(UserAdminSerializer(user).data)

        user = User.objects.all().order_by("-create_time")

        keyword = request.GET.get("keyword", None)
        if keyword:
            user = user.filter(Q(username__icontains=keyword) |
                               Q(userprofile__real_name__icontains=keyword) |
                               Q(email__icontains=keyword))
        return self.success(self.paginate_data(request, user, UserAdminSerializer))

    @super_admin_required
    def delete(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Invalid Parameter, id is required")
        ids = id.split(",")
        if str(request.user.id) in ids:
            return self.error("Current user can not be deleted")
        User.objects.filter(id__in=ids).delete()
        return self.success()


class GenerateUserAPI(APIView):
    @super_admin_required
    def get(self, request):
        """
        download users excel
        """
        file_id = request.GET.get("file_id")
        if not file_id:
            return self.error("Invalid Parameter, file_id is required")
        if not re.match(r"^[a-zA-Z0-9]+$", file_id):
            return self.error("Illegal file_id")
        file_path = f"/tmp/{file_id}.xlsx"
        if not os.path.isfile(file_path):
            return self.error("File does not exist")
        with open(file_path, "rb") as f:
            raw_data = f.read()
        os.remove(file_path)
        response = HttpResponse(raw_data)
        response["Content-Disposition"] = f"attachment; filename=users.xlsx"
        response["Content-Type"] = "application/xlsx"
        return response

    @validate_serializer(GenerateUserSerializer)
    @super_admin_required
    def post(self, request):
        """
        Generate User
        """
        data = request.data
        number_max_length = max(len(str(data["number_from"])), len(str(data["number_to"])))
        if number_max_length + len(data["prefix"]) + len(data["suffix"]) > 32:
            return self.error("Username should not more than 32 characters")
        if data["number_from"] > data["number_to"]:
            return self.error("Start number must be lower than end number")

        file_id = rand_str(8)
        filename = f"/tmp/{file_id}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:B", 20)
        worksheet.write("A1", "Username")
        worksheet.write("B1", "Password")
        i = 1

        user_list = []
        for number in range(data["number_from"], data["number_to"] + 1):
            raw_password = rand_str(data["password_length"])
            user = User(username=f"{data['prefix']}{number}{data['suffix']}", password=make_password(raw_password))
            user.raw_password = raw_password
            user_list.append(user)

        try:
            with transaction.atomic():

                ret = User.objects.bulk_create(user_list)
                UserProfile.objects.bulk_create([UserProfile(user=user) for user in ret])
                for item in user_list:
                    worksheet.write_string(i, 0, item.username)
                    worksheet.write_string(i, 1, item.raw_password)
                    i += 1
                workbook.close()
                return self.success({"file_id": file_id})
        except IntegrityError as e:
            # Extract detail from exception message
            #    duplicate key value violates unique constraint "user_username_key"
            #    DETAIL:  Key (username)=(root11) already exists.
            return self.error(str(e).split("\n")[1])
