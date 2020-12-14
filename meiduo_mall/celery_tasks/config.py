# Celery配置文件
import global_config

# 指定中间人, 消息队列, 任务队列, 容器, 使用redis
broker_url = global_config.REDIS_URL_CELERY
