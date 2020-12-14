# Celery入口
from celery import Celery

# 创建Celery实例
celery_app = Celery('meiduo')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])

# 启动Celery进程命令: celery -A Celery入口 工作进程 -l 日志级别
# 在celery_tasks的同级目录下,输入以下命令即可:
# celery -A celery_tasks.main worker -l info
