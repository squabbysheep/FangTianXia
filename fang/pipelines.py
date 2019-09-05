from scrapy.exporters import JsonLinesItemExporter
import pymongo


class FangPipeline(object):
    def __init__(self):
        self.newhouse_fp = open('newhouse.json', 'wb')
        self.esfhouse_fp = open('esfhouse.json', 'wb')
        self.newhouse_exporter = JsonLinesItemExporter(self.newhouse_fp, ensure_ascii=False)
        self.esfhouse_exporter = JsonLinesItemExporter(self.esfhouse_fp, ensure_ascii=False)

    def process_item(self, item, spider):
        self.newhouse_exporter.export_item(item)
        self.esfhouse_exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.newhouse_fp.close()
        self.esfhouse_fp.close()


# 保存到mongodb
class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db, mongo_username, mongo_password):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_username = mongo_username
        self.mongo_password = mongo_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_username=crawler.settings.get('MONGO_USERNAME'),
            mongo_password=crawler.settings.get('MONGO_PASSWORD'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, username=self.mongo_username, password=self.mongo_password)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.collection
        # self.db[name].insert(dict(item))
        # 根据唯一url进行数据更新
        self.db[name].update({'origin_url': item.get('origin_url')}, {'$set': item}, True)
        return item

    def close_spider(self, spider):
        self.client.close()


# 保存到MySQL
from twisted.enterprise import adbapi  # enterprise:事业、企业
import MySQLdb.cursors


class MysqlTwistedPipline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],  # host、db、user、passwd...必须写死 ，和底层代码一一对应 （passwd  password）
            db=settings["MYSQL_DATABASE"],  # 因此下边的table不能传入
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = 'insert into %s(%s) value(%s)' % (item.collection, keys, values)  # 数据库表名从items.py
        cursor.execute(sql, tuple(data.values()))
