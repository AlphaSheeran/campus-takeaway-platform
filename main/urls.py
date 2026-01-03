from django.urls import path
from .views import UserRegisterView, UserLoginView, AddressManageView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user_register"),
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("address/manage/", AddressManageView.as_view(), name="address_manage"),
]

urlpatterns = [
    path("register/", MerchantRegisterView.as_view(), name="merchant_register"),
]

from .views import MerchantRegisterView, DishManageView, MerchantOrderHandleView

urlpatterns = [
    path("register/", MerchantRegisterView.as_view(), name="merchant_register"),
    path("dish/manage/", DishManageView.as_view(), name="dish_manage"),
    path("order/handle/", MerchantOrderHandleView.as_view(), name="merchant_order_handle"),
]

from django.urls import path
from .views import (
    MerchantRegisterView, 
    DishManageView, 
    MerchantOrderHandleView,
    AdminMerchantAuditView
)

urlpatterns = [
    # 商家注册
    path("register/", MerchantRegisterView.as_view(), name="merchant_register"),
    # 菜品管理
    path("dish/manage/", DishManageView.as_view(), name="dish_manage"),
    # 商家订单处理
    path("order/handle/", MerchantOrderHandleView.as_view(), name="merchant_order_handle"),
    # 管理员商家审核
    path("admin/merchant/audit/", AdminMerchantAuditView.as_view(), name="admin_merchant_audit"),
]