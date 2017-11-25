from models import spider_58




spider = spider_58.Spider_58()

try:
    spider.run()
except Exception as e:
    print(e)
    spider.logger.error(str(e))