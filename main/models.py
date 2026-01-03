from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import re

class User(models.Model):
    """用户模型"""
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=100, verbose_name="密码")
    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    name = models.CharField(max_length=50, verbose_name="真实姓名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "ct_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    @staticmethod
    def validate_phone(phone):
        """手机号格式验证"""
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone):
            raise ValueError("手机号格式不正确")
        return True

    def set_password(self, raw_password):
        """密码加密"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """验证密码"""
        return check_password(raw_password, self.password)

class Address(models.Model):
    """用户地址模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name="所属用户")
    name = models.CharField(max_length=50, verbose_name="收件人")
    phone = models.CharField(max_length=11, verbose_name="收件人手机号")
    detail = models.CharField(max_length=200, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认地址")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "ct_address"
        verbose_name = "用户地址"
        verbose_name_plural = verbose_name