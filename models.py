from django.db import models
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