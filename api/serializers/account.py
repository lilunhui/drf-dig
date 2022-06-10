from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api import models


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(label='密码', min_length=8, write_only=True)
    confirm_password = serializers.CharField(label='确认密码', write_only=True)

    class Meta:
        model = models.UserInfo
        fields = ['username', 'phone', 'password', 'confirm_password']

    def validate_username(self, value):
        exists = models.UserInfo.objects.filter(username=value, deleted=False).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return value

    def validate_phone(self, value):
        exists = models.UserInfo.objects.filter(phone=value, deleted=False).exists()
        if exists:
            raise ValidationError('手机号已被注册')
        return value

    def validate_confirm_password(self, value):
        # self.validated_data 是 校验之后用的，校验之前数据在 self.initial_data 里
        if value == self.initial_data.get('password'):
            return value
        raise ValidationError('俩次密码不一致')


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(label='用户名', write_only=True, required=False)  # required该字段不是必须输入
    phone = serializers.CharField(label='手机号', write_only=True, required=False)
    password = serializers.CharField(label='密码', min_length=8, write_only=True)

    def validate_username(self, value):
        username = self.initial_data.get('username')
        phone = self.initial_data.get('phone')
        if not username and not phone:
            raise ValidationError('用户名或手机号为空')
        if username and phone:
            raise ValidationError('提交数据异常')
        return value
