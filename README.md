# meiduo_project
django美多商城



## 一. 启动项目

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

### 3. 修改主机Host文件
```text
127.0.0.1 www.meiduo.site
```

### 4. 启动Celery任务
在`manage.py`同级目录下,执行: 
```shell script
celery -A celery_tasks.main worker -l info
```

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



