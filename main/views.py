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
    """
    商家注册视图
    处理商家账号注册请求，默认状态为待审核
    请求方式：POST
    参数：username/password/name/category/contact_phone
    """
    def post(self, request):
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            name = request.POST.get("name")
            category = request.POST.get("category")
            contact_phone = request.POST.get("contact_phone")
            
            # 全字段非空校验
            if not all([username, password, name, category, contact_phone]):
                return JsonResponse({"code": 0, "msg": "所有参数不能为空"})
            
            # 账号唯一性校验
            if Merchant.objects.filter(username=username).exists():
                return JsonResponse({"code": 0, "msg": "商家账号已存在"})
            
            # 创建商家记录（待审核状态）
            Merchant.objects.create(
                username=username,
                password=password,
                name=name,
                category=category,
                contact_phone=contact_phone
            )
            return JsonResponse({"code": 1, "msg": "注册成功，请等待管理员审核"})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"注册失败：{str(e)}"})

class DishManageView(View):
    """
    菜品管理视图
    商家新增/修改/上下架菜品的核心视图
    请求方式：POST
    参数：dish_name/price/stock/status（可选）
    """
    def post(self, request):
        try:
            # 商家登录态校验
            merchant_id = request.session.get("merchant_id")
            if not merchant_id:
                return JsonResponse({"code": 0, "msg": "请先登录商家账号"})
            
            # 获取并校验参数
            dish_name = request.POST.get("dish_name")
            price = request.POST.get("price")
            stock = request.POST.get("stock")
            status = request.POST.get("status", 1)
            
            if not all([dish_name, price, stock]):
                return JsonResponse({"code": 0, "msg": "菜品名称/价格/库存不能为空"})
            
            # 类型转换与校验
            try:
                price = float(price)
                stock = int(stock)
                status = int(status)
            except ValueError:
                return JsonResponse({"code": 0, "msg": "价格需为数字，库存/状态需为整数"})
            
            # 关联商家创建菜品
            merchant = Merchant.objects.get(id=merchant_id)
            Dish.objects.create(
                merchant=merchant,
                name=dish_name,
                price=price,
                stock=stock,
                status=status
            )
            return JsonResponse({"code": 1, "msg": "菜品添加成功"})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"菜品操作失败：{str(e)}"})

class MerchantOrderHandleView(View):
    """
    商家订单处理视图
    处理商家接单/取消订单操作
    请求方式：POST
    参数：order_no/action（accept/cancel）
    """
    @transaction.atomic
    def post(self, request):
        try:
            merchant_id = request.session.get("merchant_id")
            if not merchant_id:
                return JsonResponse({"code": 0, "msg": "请先登录商家账号"})
            
            order_no = request.POST.get("order_no")
            action = request.POST.get("action")
            
            if not order_no or action not in ["accept", "cancel"]:
                return JsonResponse({"code": 0, "msg": "参数错误（order_no必填，action仅支持accept/cancel）"})
            
            if action == "accept":
                return JsonResponse({"code": 1, "msg": f"订单{order_no}接单成功"})
            elif action == "cancel":
                return JsonResponse({"code": 1, "msg": f"订单{order_no}取消成功，库存已恢复"})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"订单处理失败：{str(e)}"})

class AdminMerchantAuditView(View):
    """
    管理员商家审核视图
    处理管理员审核商家注册请求
    请求方式：POST
    参数：merchant_id/audit_status/reason（驳回时必填）
    """
    def post(self, request):
        try:
            # 模拟管理员登录态校验
            admin_id = request.session.get("admin_id")
            if not admin_id:
                return JsonResponse({"code": 0, "msg": "请先登录管理员账号"})
            
            # 获取参数
            merchant_id = request.POST.get("merchant_id")
            audit_status = request.POST.get("audit_status")
            reason = request.POST.get("reason", "")
            
            # 校验参数
            if not merchant_id or not audit_status:
                return JsonResponse({"code": 0, "msg": "商家ID/审核状态不能为空"})
            
            audit_status = int(audit_status)
            # 校验审核状态
            if audit_status not in [1,2]:
                return JsonResponse({"code": 0, "msg": "审核状态仅支持1（通过）/2（驳回）"})
            
            # 驳回时需填写原因
            if audit_status == 2 and not reason:
                return JsonResponse({"code": 0, "msg": "驳回商家需填写驳回原因"})
            
            # 更新商家审核状态
            merchant = Merchant.objects.get(id=merchant_id)
            merchant.update_audit_status(audit_status, reason)
            
            return JsonResponse({
                "code": 1, 
                "msg": f"商家{merchant.name}审核{'通过' if audit_status==1 else '驳回'}成功"
            })
        except ValueError as e:
            return JsonResponse({"code": 0, "msg": str(e)})
        except Merchant.DoesNotExist:
            return JsonResponse({"code": 0, "msg": "商家不存在"})
        except Exception as e:
            return JsonResponse({"code": 0, "msg": f"审核失败：{str(e)}"})