from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import re
import uuid
from datetime import datetime
from django.db import models
# -------------------------- 用户模块 --------------------------
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
    def validate_phone(phone: str) -> bool:
        """
        手机号格式验证
        :param phone: 手机号字符串
        :return: 验证通过返回True，否则抛出ValueError
        """
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone):
            raise ValueError("手机号格式不正确（需为11位有效手机号）")
        return True

    def set_password(self, raw_password: str) -> None:
        """密码加密存储"""
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    def check_password(self, raw_password: str) -> bool:
        """验证密码是否正确"""
        return check_password(raw_password, self.password)


class Address(models.Model):
    """用户地址模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="addresses", 
        verbose_name="所属用户"
    )
    name = models.CharField(max_length=50, verbose_name="收件人")
    phone = models.CharField(max_length=11, verbose_name="收件人手机号")
    detail = models.CharField(max_length=200, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认地址")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "ct_address"
        verbose_name = "用户地址"
        verbose_name_plural = verbose_name

# -------------------------- 订单模块 --------------------------
class Order(models.Model):
    """订单主表"""
    ORDER_STATUS = (
        (0, "待支付"),
        (1, "已支付"),
        (2, "已接单"),
        (3, "已完成"),
        (4, "已取消")
    )
    order_no = models.CharField(
        max_length=32, 
        unique=True, 
        default=lambda: uuid.uuid4().hex[:16] + datetime.now().strftime("%Y%m%d%H%M%S"),
        verbose_name="订单号"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="orders", 
        verbose_name="下单用户"
    )
    total_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="订单总金额"
    )
    status = models.IntegerField(
        choices=ORDER_STATUS, 
        default=0, 
        verbose_name="订单状态"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    class Meta:
        db_table = "ct_order"
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def update_status(self, target_status: int) -> None:
        """更新订单状态"""
        if target_status not in [0,1,2,3,4]:
            raise ValueError("订单状态值不合法")
        self.status = target_status
        if target_status == 1:  # 已支付
            self.pay_time = datetime.now()
        self.save(update_fields=["status", "pay_time"])


class OrderItem(models.Model):
    """订单项（订单明细）"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="items", 
        verbose_name="所属订单"
    )
    dish_name = models.CharField(max_length=100, verbose_name="菜品名称")
    quantity = models.IntegerField(default=1, verbose_name="菜品数量")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="菜品单价")
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="小计金额")

    class Meta:
        db_table = "ct_order_item"
        verbose_name = "订单项"
        verbose_name_plural = verbose_name



class Merchant(models.Model):
    """商家模型"""
    MERCHANT_STATUS = (
        (0, "待审核"),
        (1, "审核通过"),
        (2, "审核驳回")
    )
    username = models.CharField(max_length=50, unique=True, verbose_name="商家账号")
    password = models.CharField(max_length=100, verbose_name="密码")
    name = models.CharField(max_length=100, verbose_name="店铺名称")
    category = models.CharField(max_length=50, verbose_name="店铺分类（快餐/奶茶等）")
    contact_phone = models.CharField(max_length=11, verbose_name="联系电话")
    status = models.IntegerField(choices=MERCHANT_STATUS, default=0, verbose_name="审核状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "ct_merchant"
        verbose_name = "商家"
        verbose_name_plural = verbose_name

class Dish(models.Model):
    """菜品模型"""
    DISH_STATUS = (
        (0, "下架"),
        (1, "上架")
    )
    merchant = models.ForeignKey(
        Merchant, 
        on_delete=models.CASCADE, 
        related_name="dishes", 
        verbose_name="所属商家"
    )
    name = models.CharField(max_length=100, verbose_name="菜品名称")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="菜品单价")
    stock = models.IntegerField(default=0, verbose_name="菜品库存")
    status = models.IntegerField(choices=DISH_STATUS, default=1, verbose_name="上下架状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "ct_dish"
        verbose_name = "菜品"
        verbose_name_plural = verbose_name

    def reduce_stock(self, quantity: int) -> bool:
        """
        扣减库存（修复：判断负数）
        :param quantity: 扣减数量
        :return: 扣减成功返回True，失败返回False
        """
        if quantity <= 0:
            raise ValueError("扣减数量必须大于0")
        if self.stock < quantity:
            raise ValueError("库存不足，无法扣减")
        self.stock -= quantity
        self.save(update_fields=["stock"])
        return True