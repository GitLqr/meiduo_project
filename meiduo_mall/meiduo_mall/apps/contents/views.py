from collections import OrderedDict

from django.shortcuts import render
# Create your views here.
from django.views import View

from contents.models import ContentCategory
from contents.utils import get_categories


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""

        categories = get_categories()

        # 查询首页广告数据
        # 查询所有的广告类别
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html', context)
