import base64
import json
import pickle

from django import http
from django.shortcuts import render
from django_redis import get_redis_connection

# Create your views here.
from django.views import View

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')

            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            redis_sku_ids = redis_cart.keys()
            if selected:
                redis_conn.sadd('selected_%s' % user.id, *redis_sku_ids)
            else:
                redis_conn.srem('selected_%s' % user.id, *redis_sku_ids)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            cart_str = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            if cart_str:
                # 将 cart_str 转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)

                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected

                # 将cart_dict转成bytes类型的字典
                cart_dict_bytes = pickle.dumps(cart_dict)
                # 将cart_dict_bytes转成bytes类型的字符串
                cart_str_bytes = base64.b64encode(cart_dict_bytes)
                # 将cart_str_bytes转成字符串
                cookie_cart_str = cart_str_bytes.decode()

                response.set_cookie('carts', cookie_cart_str)

            return response


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """保存购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if not all([sku_id, count, selected]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户已登录, 操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 需要以增量计算的形式保存商品数据
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 保存商品勾选状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 如果用户未登录, 操作cookie购物车
            # 获取cookie中的购物车数据, 并且判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将 cart_str 转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 判断当前要添加的商品在cart_dict中是否存在
            if sku_id in cart_dict:
                # 购物车已存在, 增量计算
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cart_dict转成bytes类型的字典
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 将cart_dict_bytes转成bytes类型的字符串
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 将cart_str_bytes转成字符串
            cookie_cart_str = cart_str_bytes.decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def get(self, request):
        """查询购物车"""
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录, 查询redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            # 将redis_cart和redis_selected进行数据结构的构造, 合并数据, 数据结构跟未登录用户购物车结构一致
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_selected
                }
        else:
            # 用户未登录, 查询cookies购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将 cart_str 转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

        # 构造响应数据
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })
        context = {
            'cart_skus': cart_skus
        }
        return render(request, 'cart.html', context)

    def put(self, request):
        """修改购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if not all([sku_id, count, selected]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()

            # 由于后端收到的数据是最终的结果, 所以覆盖写入
            pl.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将 cart_str 转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 由于后端收到的数据是最终的结果, 所以覆盖写入
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url
            }

            # 将cart_dict转成bytes类型的字典
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 将cart_dict_bytes转成bytes类型的字符串
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 将cart_str_bytes转成字符串
            cookie_cart_str = cart_str_bytes.decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def delete(self, request):
        """删除购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录, 删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录, 删除cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将 cart_str 转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            if sku_id in cart_dict:
                del cart_dict[sku_id]

                # 将cart_dict转成bytes类型的字典
                cart_dict_bytes = pickle.dumps(cart_dict)
                # 将cart_dict_bytes转成bytes类型的字符串
                cart_str_bytes = base64.b64encode(cart_dict_bytes)
                # 将cart_str_bytes转成字符串
                cookie_cart_str = cart_str_bytes.decode()

                response.set_cookie('carts', cookie_cart_str)

            return response
