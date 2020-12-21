import os
from collections import OrderedDict

from django.conf import settings
from django.template import loader

from contents.models import ContentCategory
from contents.utils import get_categories


def generate_static_index_html():
    """静态化首页"""
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

    # 渲染模板
    template = loader.get_template('index.html')
    html_text = template.render(context)
    # 将模板文件写入到静态路径
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
