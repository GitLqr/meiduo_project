# Create your views here.
import logging

from django import http
from django.views import View

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


class AreasView(View):
    """省市区三级联动"""

    def get(self, request):
        # 判断当前是要查询省份数据还是市区数据
        area_id = request.GET.get('area_id')
        if not area_id:
            try:
                # 查询省级数据
                province_model_list = Area.objects.filter(parent__isnull=True)

                # 需要将模型列表转成字典列表
                province_list = []
                for province_model in province_model_list:
                    province_dict = {
                        'id': province_model.id,
                        'name': province_model.name
                    }
                    province_list.append(province_dict)

                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})
        else:
            try:
                # 查询城市或区县数据
                parent_model = Area.objects.get(id=area_id)
                # sub_model_list = parent_model.area_set.all()
                sub_model_list = parent_model.subs.all()  # Area模型中指定了别名related_name为subs

                subs = []
                for sub_model in sub_model_list:
                    sub_dict = {
                        'id': sub_model.id,
                        'name': sub_model.name
                    }
                    subs.append(sub_dict)
                sub_data = {
                    'id': parent_model.id,
                    'name': parent_model.name,
                    'subs': subs
                }

                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询城市或区县数据错误'})
