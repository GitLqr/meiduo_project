MY_SERVER_HOST = '192.168.2.162'

# mysql配置
MYSQL_HOST = MY_SERVER_HOST
MYSQL_PORT = '3306'

# redis配置
REDIS_HOST = MY_SERVER_HOST
REDIS_PORT = '6379'
REDIS_URL = 'redis://%s:%s/' % (REDIS_HOST, REDIS_PORT)
REDIS_URL_DEFAULT = REDIS_URL + '0'
REDIS_URL_SESSION = REDIS_URL + '1'
REDIS_URL_VERIFY_CODE = REDIS_URL + '2'
REDIS_URL_HISTORY = REDIS_URL + '3'
REDIS_URL_CARTS = REDIS_URL + '4'
REDIS_URL_CELERY = REDIS_URL + '10'

# FastDFS配置
FDFS_URL_PREFIX = 'http://' + MY_SERVER_HOST + ':8888/'

# Elasticsearch配置
ELASTICSEARCH_URL = 'http://' + MY_SERVER_HOST + ':9200/'
