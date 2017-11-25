from models import spider_anjuke_ershoufang


spider = spider_anjuke_ershoufang.Spider_anjuke()

try:
    spider.run()
except Exception as e:
    print(e)
    spider.logger.error(str(e))