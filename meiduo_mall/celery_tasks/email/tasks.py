from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


# bind: 保证task对象会作为第一个参数自动传入
# name: 异步任务别名
# retry_backoff: 异常自动重试的时间间隔, 第n次( retry_backoff * 2^(n-1) )s
# max_retries: 异常自动重试次数的上限
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """定义发送验证邮件的任务"""
    # send_mail('标题', '普通邮件正文', '收件人', '收件人列表', '富文本邮件正文(html)')
    subject = '美多商城邮箱验证'
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s，请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s</a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        # 触发错误重试: 最多重试3次
        raise self.retry(exc=e, max_retries=3)
