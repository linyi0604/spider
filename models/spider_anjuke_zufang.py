import time
from log import log
import random
import requests
from lxml import etree
import settings
from data_base.save import save

'''
爬取安居客租房 经纪人信息
'''
class Spider_anjuke(object):
    def __init__(self):
        self.start_url = 'https://bj.zu.anjuke.com/?from=navigation'
        self.logger = log.Logger('log/anjuke.zufang.log','安居客租房爬虫')
        self.sleep_time = settings.sleep_time
        self.headers = settings.HEADERS
        self.total = 0
        self.retry_time = settings.RETRY_TIME

    def parse_url(self,url,proxies=None):
        '''爬取指定url代码 返回结构化的etree'''
        random_time = random.randint(self.sleep_time//2,self.sleep_time*2)
        time.sleep(random_time)
        self.logger.info("正在获取链接：%s" % url)
        try:
            header = random.choice(self.headers)
            response = requests.get(url=url, headers=header, proxies=proxies, timeout=10)

            assert response.status_code == 200

            self.logger.info("成功获取链接：" + url)
            self.retry_time = settings.RETRY_TIME
            return etree.HTML(response.content)
        except Exception as e:
            if self.retry_time > 0:
                self.logger.error('发送请求发生异常,再次尝试,请求地址:%s' % url)
                self.retry_time -= 1
                self.parse_url(url)
            else:
                self.retry_time = settings.RETRY_TIME
                self.logger.error('尝试' + str(settings.RETRY_TIME) + '次请求仍然失败,请求地址:%s' % url)
                self.logger.error('错误信息:' + str(e))
                return None

    def get_content_list(self,xhtml):
        if xhtml is None :
            self.logger.info('本条抓取失败,网络状态不好或被反爬,本条忽略,继续向下')
            return None
        div_list = xhtml.xpath('//div[@class="zu-info"]')
        content_list = []
        for div in div_list:
            con = {}
            # 获取当前信息的链接
            href = div.xpath('./h3/a/@href')
            con["href"] = href[0] if href else None
            content_list.append(con)
        return content_list

    def get_next_page(self,xhtml):
        try:
            next_page = xhtml.xpath('.//a[@class="aNxt"]/@href')
            next_page = next_page[0] if next_page else None
            self.logger.info('获取下一页地址为:'+next_page)
            return next_page
        except Exception as e:
            # print(e)
            self.logger.error('全部数据爬取完成' )

    def save(self,con):
        '''保存功能'''
        try:
            info = save(con)
            self.total += 1
            self.logger.info('已成功获取数据数量:'+str(self.total))
            self.logger.info(info)
        except Exception as e:
            print(e)
            self.logger.info('存储数据发生错误:'+str(e))

    def get_detail_info(self,con):
        self.logger.info('尝试获取一条信息详情:'+str(con['href']))
        xhtml = self.parse_url(con["href"])
        con['name'] = None
        con['phone'] = None
        con['head_picture_href'] = None
        con['head_picture_href'] = None
        con['agency_name'] = None
        con['store_name'] = None
        if xhtml is None:
            self.logger.info('性情页面获取失败,网络不好或被反爬:'+str(con['href']))
        try:
            self.logger.info("尝试获取详细信息！")
            # 获取经纪人姓名
            name = xhtml.xpath('//h2[@id="broker_true_name"]/text()')
            con['name'] = name[0] if name else None
            #获取电话号码
            phone = xhtml.xpath('//p[@class="broker-mobile"]/text()')
            con['phone'] = phone[0].replace(' ','') if phone else None
            # 获取头像链接
            head = xhtml.xpath('//a[@class="broker_pic"]/img/@src')
            con['head_picture_href'] = head[0] if head else None
            # 获取经纪人所在公司和门店
            agency = xhtml.xpath('//div[@class="broker-company"]/p')
            agency_name = agency[0].xpath('./a/text()') if agency else None
            # 公司
            con['agency_name'] = agency_name[0] if agency_name else None
            #　门店
            store_name = agency[1].xpath('./a/text()') if agency else None
            con['store_name'] = store_name[0] if store_name else None
            self.logger.info('详细信息获取成功')
        except Exception as e:
            self.logger.error('获取详细信息发生错误:'+str(e))
            self.logger.info('忽略当前，继续向下')



    def run(self):
        next_page = self.start_url

        while next_page is not None:
            xhtml = self.parse_url(next_page)
            if xhtml is None:
                self.logger.info('网络状态不好或被反爬,忽略当前,继续向下')
            else :
                content_list = self.get_content_list(xhtml)
                for con in content_list:
                    con['name']=None
                    con['phone'] = None
                    self.get_detail_info(con)
                    print('安居客租房:',con['name'],con['phone'])
                    self.save(con)
            print('本页结束 翻页!')
            next_page = self.get_next_page(xhtml)


if __name__ == '__main__':
    s = Spider_anjuke()
    s.run()