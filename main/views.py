from django.http import JsonResponse
from django.views import View
from .models import User

class UserRegisterView(View):
    """用户注册视图"""
    def post(self, request):
        try:
            # 获取前端参数
            username = request.POST.get("username")
            password = request.POST.get("password")
            phone = request.POST.get("phone")
            name = request.POST.get("name")
            
            # 手机号验证
            User.validate_phone(phone)
            
            # 检查用户名/手机号是否已存在
            if User.objects.filter(username=username).exists():
                return JsonResponse({"code": 0, "msg": "用户名已存在"})
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({"code": 0, "msg": "手机号已注册"})
            
            # 创建用户
            User.objects.create(
                username=username,
                password=password,  # 暂未加密，后续修复
                phone=phone,
                name=name
            )
            return JsonResponse({"code": 1, "msg": "注册成功"})
        except ValueError as e:
            return JsonResponse({"code": 0, "msg": str(e)})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"注册失败：{str(e)}"})