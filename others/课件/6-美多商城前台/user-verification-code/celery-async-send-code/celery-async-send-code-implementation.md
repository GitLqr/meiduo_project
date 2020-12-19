# Celery异步发送短信

### 1. 定义Celery包

<img src="/user-verification-code/images/28定义celery包.png" style="zoom:50%">

### 2. 创建Celery实例并加载配置

> 1.创建Celery实例

<img src="/user-verification-code/images/29celery入口文件.png" style="zoom:50%">

> main.py

```python
# celery启动文件
from celery import Celery


# 创建celery实例
celery_app = Celery('meiduo')
```

> 2.加载Celery配置

<img src="/user-verification-code/images/30celery配置文件.png" style="zoom:50%">

> config.py

```python
# celery配置文件


# 指定任务队列的位置
broker_url = "redis://127.0.0.1/10"
# 指定任务执行结果保存的位置
result_backend='redis://127.0.0.1/11'
```

> main.py

```python
# celery启动文件
from celery import Celery


# 创建celery实例
celery_app = Celery('meiduo')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')
```

### 3. 定义发送短信异步任务

<img src="/user-verification-code/images/31定义发送短信异步任务.png" style="zoom:50%">

> main.py

```python
# celery启动文件
from celery import Celery


# 创建celery实例
celery_app = Celery('meiduo')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])
```

> sms.tasks.py

```python
# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@celery_app.task(bind=True, name='ccp_send_sms_code', retry_backoff=3)
def ccp_send_sms_code(self, mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 0 或 -1
    """
    try:
        send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
    except Exception as e:
        logger.error(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
    if send_ret != 0:
        # 有异常自动重试三次
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)

    return send_ret
```

### 4. 调用发送短信异步任务
```python
# 发送短信验证码
# CCP().send_template_sms(mobile,[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
# Celery异步发送短信验证码
ccp_send_sms_code.delay(mobile, sms_code)
```

### 5. 启动Celery服务器
<img src="/user-verification-code/images/32启动celery效果.png" style="zoom:50%">

<img src="/user-verification-code/images/33celery执行异步任务效果.png" style="zoom:50%">