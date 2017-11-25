from models import spider_anjuke_zufang


spider = spider_anjuke_zufang.Spider_anjuke()

try:
    spider.run()
except Exception as e:
    print(e)
    spider.logger.error(str(e))