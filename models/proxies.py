import requests
from lxml import etree
import random
import time
import settings
from log import log

class MyProxies(object):
    def __init__(self):
        self.url = 'http://www.kuaidaili.com/free/inha/'
        self.headers = settings.HEADERS
        self.logger = log.Logger('../log/ip_proxy.log','ip代理爬虫')
        self.ip_list = []
        self.retry = settings.RETRY_TIME

    def get_ip_list(self):
        try :
            self.logger.info('尝试获取ip列表')
            response = requests.get(url=self.url,headers=random.choice(self.headers),timeout=10)
            xhtml = etree.HTML(response.content)
            tr_list = xhtml.xpath('.//div[@id="list"]/table/tbody/tr')
            for tr in tr_list:
                ip = tr.xpath('.//td')
                ip = ( ip[0].xpath('./text()')[0],ip[1].xpath('./text()')[0],ip[3].xpath('./text()')[0] )
                ip = {
                    ip[2].lower():ip[2].lower()+"://"+ip[0]+":"+ip[1]
                }
                self.ip_list.append(ip)
            self.logger.info('成功获取ip列表')
        except Exception as e:
            # time.sleep(settings.sleep_time)
            self.logger.error(e)
            self.get_ip_list()


    def get_ip(self):
        if len( self.ip_list ) < 3:
            self.get_ip_list()

        ip = self.ip_list.pop(0)
        return ip



if __name__ == '__main__':
    m = MyProxies( )
    while True:
        print(m.get_ip())

