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
 