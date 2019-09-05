import datetime

BOT_NAME = 'fang'
SPIDER_MODULES = ['fang.spiders']
NEWSPIDER_MODULE = 'fang.spiders'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 0.1
CONCURRENT_REQUESTS = 16

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

ITEM_PIPELINES = {
    # 'fang.pipelines.FangPipeline': 300,
    # 'fang.pipelines.MongoPipeline': 400,
    'fang.pipelines.MysqlTwistedPipline': 420,
}

DOWNLOADER_MIDDLEWARES = {
    'fang.middlewares.UserAgent': 300,
    'fang.middlewares.ProxyMiddleware': 301,
    'fang.middlewares.CaptchaMiddleware': 302,
}

# 1、确保request存储到redis中
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 2、确保所有爬虫共享相同的去重指纹
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 3、在redis中保持scrapy-redis用到的队列，不会清理redis中的队列，从而可以实现暂停和恢复的功能。
SCHEDULER_PERSIST = True

# A、建立redis连接
# 设置连接redis信息，mast主机ip，此处为腾讯云ip
# REDIS_HOST = '139.155.96.221'
# REDIS_PORT = 6379
# 如果redis数据库有密码，使用如下方法：
REDIS_URL = 'redis://:Re_Lei@129.28.200.147:6379'

# B、建立MongoDB连接
MONGO_URI = '129.28.200.147'
MONGO_DB = 'fangtianxia'
# 在CentOs下写入数据需要使用账号密码连接
MONGO_USERNAME = 'root'
MONGO_PASSWORD = 'Mongo_Lei'
# MONGO_URL = 'mongodb://root:123456@192.168.43.68:27017'

# C、建立MySQL连接
MYSQL_HOST = 'localhost'
MYSQL_DATABASE = 'fangtianxia'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Sql_Lei'

# D、代理url
PROXY_URL = 'http://129.28.200.147:5557/random'

# E、设置日志级别，保存信息
# LOG_LEVEL = "INFO"

startDate = datetime.datetime.now().strftime('%Y%m%d')
LOG_FILE = f"EsfHouse{startDate}.txt"

# F、设置最大等待时间、失败重试次数
# 默认响应时间是180s，长时间不释放会占用一个并发量影响效率
DOWNLOAD_TIMEOUT = 10
# 是否进行失败重试
RETRY_ENABLED = True
# 失败重试的次数，连续失败3次后会抛出TimeOut异常被errback捕获
RETRY_TIMES = 3
