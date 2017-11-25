from models import spider_ganji


spider = spider_ganji.Spider_ganji()

try:
    spider.run()
except Exception as e:
    print(e)
    spider.logger.error(str(e))