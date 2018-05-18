# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import csv
import json
import logging.handlers

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


LOG_FILE = r"error.log"
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)
fmt = '[%(levelname)s] %(asctime)s %(name)s: %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger("daily_chart")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class TedJsonPipeline:
    def __init__(self):
        self.file = codecs.open("ted_data.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def close_spider(self, spider):
        self.file.close()


class TedMysqlPipeline(object):
    '''
    保存到数据库中对应的class
    1、在settings.py文件中配置
    2、在自己实现的爬虫类中yield item,会自动执行
    '''

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        # 读取settings中配置的数据库参数
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    # pipeline默认调用
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法
        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item

    # 写入数据库中
    # SQL语句在这里
    def _conditional_insert(self, tx, item):
        sql = "insert into video_media(url,pic_url,title,intro,like_num,comment_num,view_num,source,update_time,duration,tag) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = (
            item['url'], item['pic_url'], item['title'], item['intro'], item['like_num'], item['comment_num'],
            item['view_num'],
            item['source'], item["update_time"], item['duration'], item['tag'])
        tx.execute(sql, params)

    # 错误处理方法
    def _handle_error(self, failue, item, spider):
        logger.error(failue)



class CSVPipeline(object):

    def __init__(self):
        self.csvwriter = csv.writer(open('items.csv', 'wb'), delimiter=',')
        # self.csvwriter.writerow(
        #     ['source', 'view_num', 'intro', 'like_num', 'comment_num', 'update_time', 'tag', 'url', 'pic_url', 'title',
        #      'duration'])

    def process_item(self, item, ampa):
        rows = zip(item['source'], item['view_num'], item['intro'], item['comment_num'], item['update_time'],
                   item['tag'], item['url'], item['pic_url'], item['title'], item['duration'])

        for row in rows:
            self.csvwriter.writerow(row)

        return item


