def get_breadcrumb(category):
    """
    获取面包屑导航
    :param category: 类别对象: 一级, 二级, 三级
    :return: 一级: 返回一级; 二级: 返回一级+二级; 三级: 返回一级+二级+三级
    """
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': ''
    }
    if category.parent == None:  # 说明category是一级
        breadcrumb['cat1'] = category
    elif category.subs.count() == 0:  # 说明category是三级
        cat2 = category.parent
        breadcrumb['cat1'] = cat2.parent
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = category
    else:  # 说明category是二级
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category

    return breadcrumb
