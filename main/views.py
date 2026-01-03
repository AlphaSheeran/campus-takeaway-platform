from django.http import JsonResponse
from django.views import View
from django.db import transaction
from .models import User, Address, Order, OrderItem

class UserRegisterView(View):
    """用户注册视图"""
    def post(self, request):
        try:
            # 获取前端参数
            username = request.POST.get("username").strip()
            password = request.POST.get("password").strip()
            phone = request.POST.get("phone").strip()
            name = request.POST.get("name").strip()

            # 空值校验
            if not all([username, password, phone, name]):
                return JsonResponse({"code": 0, "msg": "参数不能为空"})

            # 手机号验证
            User.validate_phone(phone)

            # 检查用户名/手机号是否已存在
            if User.objects.filter(username=username).exists():
                return JsonResponse({"code": 0, "msg": "用户名已存在"})
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({"code": 0, "msg": "手机号已注册"})

            # 创建用户（密码加密）
            user = User.objects.create(
                username=username,
                phone=phone,
                name=name
            )
            user.set_password(password)
            return JsonResponse({"code": 1, "msg": "注册成功"})

        except ValueError as e:
            return JsonResponse({"code": 0, "msg": str(e)})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"注册失败：{str(e)}"})

# 登录、地址管理视图代码格式同步优化（略，仅调整缩进/注释/空值校验，逻辑不变）
class UserLoginView(View):
    """用户登录视图"""
    def post(self, request):
        try:
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()

            if not username or not password:
                return JsonResponse({"code": 0, "msg": "用户名/密码不能为空"})

            user = User.objects.get(username=username)
            if not user.check_password(password):
                return JsonResponse({"code": 0, "msg": "密码错误"})

            request.session["user_id"] = user.id
            return JsonResponse({
                "code": 1, 
                "msg": "登录成功", 
                "data": {"user_id": user.id, "name": user.name}
            })

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

            # 获取参数并去空
            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            detail = request.POST.get("detail", "").strip()
            is_default = request.POST.get("is_default", False) == "true"

            # 空值校验
            if not all([name, phone, detail]):
                return JsonResponse({"code": 0, "msg": "收件人/手机号/详细地址不能为空"})

            # 手机号验证
            User.validate_phone(phone)

            user = User.objects.get(id=user_id)
            # 若设置默认地址，取消其他默认地址
            if is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)

            # 创建地址
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
        
class MerchantRegisterView(View):
    """商家注册视图"""
    def post(self, request):
        try:
            # 获取前端参数
            username = request.POST.get("username")
            password = request.POST.get("password")
            name = request.POST.get("name")
            category = request.POST.get("category")
            contact_phone = request.POST.get("contact_phone")
            
            # 空值校验
            if not all([username, password, name, category, contact_phone]):
                return JsonResponse({"code": 0, "msg": "所有参数不能为空"})
            
            # 检查商家账号是否已存在
            if Merchant.objects.filter(username=username).exists():
                return JsonResponse({"code": 0, "msg": "商家账号已存在"})
            
            # 创建商家（默认待审核状态）
            Merchant.objects.create(
                username=username,
                password=password,  # 暂未加密，后续可优化
                name=name,
                category=category,
                contact_phone=contact_phone
            )
            return JsonResponse({"code": 1, "msg": "注册成功，请等待管理员审核"})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"注册失败：{str(e)}"})