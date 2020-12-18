# meiduo_project
django美多商城



## 一. 配置运行项目

### 1. 修改配置

在`global_config.py`文件中, 根据实际情况将各参数进行修改.

### 2. 迁移数据库

#### 1) 创建数据库
在远程Linux或windows的MYSQL数据库中创建一个项目数据库:

```mysql
create database meiduo charset=utf8;
```

#### 2) 创建表
在`manage.py`同级目录下,执行: 
```shell script
python manage.py makemigrations
python manage.py migrate
```

### 3. 导入数据库数据

在`others`目录中，找到所有sql文件，在远程MYSQL服务器上，使用终端输入如下命令：

```shell script
mysql -u账号 -p密码 meiduo < xxx.sql
```

> 例如：mysql -uroot -p123456 meiduo < areas.sql

### 4. 修改主机Host文件

```text
127.0.0.1 www.meiduo.site
```

### 4. 启动Celery任务
在`manage.py`同级目录下,执行: 
```shell script
celery -A celery_tasks.main worker -l info
```

> celery默认是进程池方式, 进程数以当前机器的CPU核数为参考, 每个CPU开四个进程, 可通过`--concurrency`或`-c`来指定进程数, 例如:
>
> `celery -A celery_tasks.main worker -l info --concurrency=20`
>
> 另外,Celery也支持将进程池方式改为协程方式(需要安装eventlet), 例如: 
>
> `pip install eventlet`
>
> `celery -A celery_tasks.main worker -l info -P eventlet -c=1000`

### 5. 启动项目

在`manage.py`同级目录下,执行: 
```shell script
python manage.py runserver
```


## 二. 解决代码报错

该项目的子应用模块存放在`meiduo_project/meiduo_mall/meiduo_mall/apps`目录下, `dev,py`中已经将该路径设置为导包路径, 所以django能在运行时正确识别到`[子应用.模块]`代码.
```python
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
```

但是编码期间, PyCharm还是会对`[子应用.模块]`代码报错, 这是因为该项目是非标准的Django工程, 而PyCharm默认只认识标准Django路径, 所以PyCharm中会有多处红线报错.
解决方法: 将meiduo_mall(第一个) 和 apps标记为 `Sources Root` 即可.
操作步骤: 右击目录-> `Make Directory as` -> `Sources Root`



