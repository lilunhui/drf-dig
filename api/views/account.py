from rest_framework.views import APIView
from api.extension.mixins import DigCreateModelMixin
from api.extension import return_code
from rest_framework.viewsets import GenericViewSet
from api.serializers.account import RegisterSerializer, AuthSerializer
from rest_framework.response import Response
from api import models
from django.db.models import Q
import uuid
import datetime

"""
1、只需要提供POST方法
2、请求进来执行DigCreateModelMixin方法
3、获取数据request.data进行校验
"""


class RegisterView(DigCreateModelMixin, GenericViewSet):
    """用户注册"""
    authentication_classes = []
    permission_classes = []
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.validated_data.pop('confirm_password')
        super().perform_create(serializer)


class AuthView(APIView):
    """用户登录"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # 1、获取提交的数据，并校验
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'code': return_code.VALIDATE_ERROR, 'data': serializer.errors})
        username = serializer.validated_data.get('username')
        phone = serializer.validated_data.get('phone')
        password = serializer.validated_data.get('password')

        user_obj = models.UserInfo.objects.filter(Q(username=username) | Q(phone=phone), password=password).first()
        if not user_obj:
            return Response({'code': return_code.VALIDATE_ERROR, 'errors': "用户名或密码错误"})

        token = str(uuid.uuid4())
        user_obj.token = token # 保存token
        # 时间期限2周
        user_obj.token_expiry_date = datetime.datetime.now() + datetime.timedelta(weeks=2)
        user_obj.save()
        return Response({"code": return_code.SUCCESS, "data": {"token": token, "name": user_obj.username}})
