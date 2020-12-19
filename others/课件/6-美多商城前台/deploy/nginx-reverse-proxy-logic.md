# Nginx反向代理动态业务

> 问题：
> * 当我们部署完Nginx静态数据后，发现动态业务无法访问。

<img src="/deploy/images/03访问动态业务失败.png" style="zoom:40%">

> 原因：
> * Nginx服务器无法找到美多商城服务器。

> 解决：
> * **部署美多商城服务器，并使用Nginx反向代理**


### 1. 部署美多商城服务器

> **1.准备生产环境配置文件**
* 复制开发环境配置文件`dev.py`到生产环境配置文件`prod.py`，并做修改。

```python
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = False

ALLOWED_HOSTS = ['www.meiduo.site']
```

> **2.准备生产环境启动文件**
* 生产环境我们是使用`meiduo_mall.wsgi.py`启动服务的。

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.prod")
```

> **3.安装`uwsgi`包**
* Django的程序通常使用`uwsgi服务器`来运行。

```bash
$ pip install uwsgi
```

> **4.准备`uwsgi服务`器配置文件**
* 新建`meiduo_mall.uwsgi.ini`配置文件

```ini
[uwsgi]
# 使用Nginx连接时使用，Django程序所在服务器地址
socket=172.16.21.25:8001
# 直接做web服务器使用，Django程序所在服务器地址
# http=172.16.21.25:8001
# 项目目录
chdir=项目路径/meiduo_project/meiduo_mall
# 项目中wsgi.py文件的目录，相对于项目目录
wsgi-file=meiduo_mall/wsgi.py
# 进程数
processes=4
# 线程数
threads=2
# uwsgi服务器的角色
master=True
# 存放进程编号的文件
pidfile=uwsgi.pid
# 日志文件
daemonize=uwsgi.log
# 指定依赖的虚拟环境
virtualenv=虚拟环境路径/.virtualenvs/meiduo_mall
```

> 5.管理`uwsgi服务器`

```bash
# 启动
$ uwsgi --ini uwsgi.ini
# 关闭
$ uwsgi --stop uwsgi.pid
```
<img src="/deploy/images/04部署uwsgi服务器.png" style="zoom:40%">

### 2. 部署Nginx服务器反向代理

> **1.修改Nginx服务器配置文件**

```bash
http {
	......
	# 美多商城服务器
	upstream meiduo {
		server 172.16.21.25:8001; # 美多商城服务器1
		# server 172.16.21.25:8002; # 美多商城服务器2
	}

	server {
		listen       80;
		server_name  www.meiduo.site;
		......
		location / {
			include uwsgi_params;
			uwsgi_pass meiduo;
		}

	}
}
```

> **2.启动Nginx服务器**

```bash
# 检查配置文件
$ sudo /usr/local/nginx/sbin/nginx -t
# 重启
sudo /usr/local/nginx/sbin/nginx -s reload
```

> **3.测试Nginx反向代理**

<img src="/deploy/images/05测试Nginx反向代理.png" style="zoom:40%">

### 3. 部署后的代码调整

> **1.邮箱的验证链接**

```python
# 邮箱验证链接（开发环境）
# EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'
# 邮箱验证链接（生产环境）
EMAIL_VERIFY_URL = 'http://www.meiduo.site/emails/verification/'
```

> **2.支付宝的回调地址**

```python
# 支付宝
ALIPAY_APPID = '2016082100308405'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
# ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/' # （开发环境）
ALIPAY_RETURN_URL = 'http://www.meiduo.site/payment/status/' # （生产环境）
```

> **3.详情页的访问方式**

```html
{# 开发环境 #}
{# <a href="{{ url('goods:detail', args=(sku.id, )) }}"><img src="{{ sku.default_image.url }}"></a> #}
{# <h4><a href="{{ url('goods:detail', args=(sku.id, )) }}">{{ sku.name }}</a></h4> #}

{# 生产环境环境 #}
<a href="/detail/{{ sku.id }}.html"><img src="{{ sku.default_image.url }}"></a>
<h4><a href="/detail/{{ sku.id }}.html">{{ sku.name }}</a></h4>
```

> **4.QQ登录的回调地址**

```python
# QQ登录参数 #（开发环境）
# QQ_CLIENT_ID = '101518219'
# QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
# QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# QQ登录参数 #（生产环境）
QQ_CLIENT_ID = '101531904'
QQ_CLIENT_SECRET = '6afc7211294442e13439b5b4b7ae9118'
QQ_REDIRECT_URI = 'http://www.meiduo.site:80/oauth_callback'
```


