from django.http import JsonResponse
from django.views import View
from django.db import transaction
from .models import User, Address

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
            
            # 创建用户（修复：密码加密）
            user = User.objects.create(
                username=username,
                phone=phone,
                name=name
            )
            user.set_password(password)  # 密码加密存储
            return JsonResponse({"code": 1, "msg": "注册成功"})
        except ValueError as e:
            return JsonResponse({"code": 0, "msg": str(e)})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"注册失败：{str(e)}"})

class UserLoginView(View):
    """用户登录视图"""
    def post(self, request):
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            
            # 查询用户
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return JsonResponse({"code": 0, "msg": "密码错误"})
            
            # 模拟登录态（实际项目用session/token）
            request.session["user_id"] = user.id
            return JsonResponse({"code": 1, "msg": "登录成功", "data": {"user_id": user.id, "name": user.name}})
        except User.DoesNotExist:
            return JsonResponse({"code": 0, "msg": "用户不存在"})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"登录失败：{str(e)}"})

class AddressManageView(View):
    """地址管理视图（新增/修改/默认地址设置）"""
    @transaction.atomic
    def post(self, request):
        try:
            user_id = request.session.get("user_id")
            if not user_id:
                return JsonResponse({"code": 0, "msg": "请先登录"})
            
            # 获取参数
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            detail = request.POST.get("detail")
            is_default = request.POST.get("is_default", False) == "true"
            
            # 验证手机号
            User.validate_phone(phone)
            
            user = User.objects.get(id=user_id)
            # 若设置默认地址，取消其他默认地址
            if is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)
            
            # 创建/修改地址（简化：仅演示新增）
            Address.objects.create(
                user=user,
                name=name,
                phone=phone,
                detail=detail,
                is_default=is_default
            )
            return JsonResponse({"code": 1, "msg": "地址添加成功"})
        except ValueError as e:
            return JsonResponse({"code": 0, "msg": str(e)})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"地址操作失败：{str(e)}"})