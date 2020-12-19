from django.shortcuts import render

# Create your views here.
from django.views import View
from django import http

from contents.utils import get_categories
from goods.models import GoodsCategory
from goods.utils import get_breadcrumb
from django.core.paginator import Paginator


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id不存在')

        # 获取sort: 如果sort没有值,取'default'
        sort = request.GET.get('sort', 'default')
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航: 一级 -> 二级 -> 三级
        breadcrumb = get_breadcrumb(category)

        # 分页和排序查询
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)

        # 创建分页器
        paginator = Paginator(skus, 5)  # 把skus进行分页, 每页5条记录
        page_skus = paginator.page(page_num)  # 获取到用户当前要看的那一页
        total_page = paginator.num_pages  # 获取总页数

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb
        }

        return render(request, 'list.html', context)
