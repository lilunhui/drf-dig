import datetime
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.extension import return_code
from api import models


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')
        if not token:
            raise AuthenticationFailed({"code": return_code.AUTH_FAILED, 'error': "认证失败"})
        user_obj = models.UserInfo.objects.filter(token=token).first()
        if not user_obj:
            raise AuthenticationFailed({"code": return_code.AUTH_FAILED, 'error': "认证失败"})
        if datetime.datetime.now() > user_obj.token_expiry_date:
            raise AuthenticationFailed({"code": return_code.AUTH_FAILED, 'error': "认证过期"})
        return user_obj, token

    def authenticate_header(self, request):
        return 'Bearer realm="API"'


#    登录，可以访问  request.user
# 不登录，也可以访问  request.user=None
class UserAnonTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get("token")
        if not token:
            return None
        user_object = models.UserInfo.objects.filter(token=token).first()
        if not user_object:
            return None

        if datetime.datetime.now() > user_object.token_expiry_date:
            return None

        return user_object, token

    def authenticate_header(self, request):
        return 'Bearer realm="API"'
