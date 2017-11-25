import settings
from lxml import etree
import requests
import random
import time
from log import log
from data_base.save import save
import re
'''
抓取 赶集网 房产经纪人信息

'''
class Spider_ganji(object):
    def __init__(self):
        self.start_url = ['http://bj.ganji.com/zufang/agent/','http://bj.ganji.com/fang/agent/']
        self.base_url = 'http://bj.ganji.com'
        self.headers = settings.HEADERS
        self.logger = log.Logger('log/ganji.log','赶集爬虫')
        self.sleep_time = settings.sleep_time
        self.retry_time = settings.RETRY_TIME
        self.total = 0


    def parse_url(self,url,proxies=None):
        '''爬取指定url代码 返回结构化的etree'''
        time.sleep(self.sleep_time)
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
                self.logger.error('尝试' + str(settings.RETRY_TIME) + '此请求仍然失败,请求地址:%s' % url)
                self.logger.error('错误信息:' + str(e))
                return None


    def get_content_list(self,xhtml):
        '''在经纪人页面上 取得每一个经纪人的element对象'''
        if xhtml is None :
            self.logger.info('本条抓取失败,网络状态不好或被反爬,本条忽略,继续向下')
            return None
        div_list = xhtml.xpath('//div[@class="f-main-list"]/div[@class="f-list-item"]')
        content_list = []
        for div in div_list:
            con = {}
            # 获取经纪人的姓名
            name = div.xpath('.//a[@class="broker-name"]/text()')
            con["name"] = name[0] if name else None
            # 获取经纪人的手机号码
            phone = div.xpath('.//p[@class="tel"]/text()')
            con['phone'] = phone[0] if phone else None
            # 获取经纪人的所在公司名称
            agency = div.xpath('.//span[contains(@class,"broker-company")]/text()')
            con["agency_name"] = agency[0] if agency else None
            # 获取经纪人头像的地址
            head = div.xpath('.//img/@src')
            con['head_picture_href'] = head[0] if head else None
            # 获取中介名词 服务区域 服务小区
            li_list = div.xpath('.//ul[@class="broker-service"]/li')
            # 数据清洗
            for li in li_list:
                info = li.xpath('.//span//text()')
                if info[0] == '经纪公司：' :
                    con['agency_name'] = info[-1]
                elif info[0] == '服务区域：' :
                    con["area"] = ''.join(info[1:] )
                elif info[0] == '服务小区：' :
                    info = info[1:]
                    for i in range(len(info)):
                        info[i] = re.sub(r'\s+','',info[i])
                    for i in range( len(info)-1 ,-1,-1 ) :
                        if info[i] == '':
                            info.remove(info[i])
                    con['dept_list'] = info
            content_list.append(con)
        return content_list

    def save(self,con):
        '''保存功能'''
        try:
            info = save(con)
            self.total += 1
            self.logger.info('已成功获取数据数量:'+str(self.total))
            self.logger.info(info)
        except Exception as e:
            # print(e)
            self.logger.info('存储数据发生错误:'+str(e))

    def get_next_page(self,xhtml):
        '''获取下一页地址'''
        try:
            next_page = xhtml.xpath('.//a[@class="next"]/@href')
            if next_page is None:
                return None
            next_page = self.base_url + next_page[0] if next_page else None
            self.logger.info('获取下一页地址为:'+next_page)
            return next_page
        except Exception as e:
            # print(e)
            self.logger.error('全部爬取完成!' )


    def run(self):
        '''开启爬虫'''
        for url in self.start_url :
            next_page = url
            while next_page is not None:
                # 获取当前页面的链接
                xhtml = self.parse_url(next_page)
                if xhtml is None:
                    self.logger.info('网络状态不好或被反爬,忽略当前,继续向下')
                    break
                content_list = self.get_content_list(xhtml)
                for con in content_list :
                    print('赶集:',con['name'],con['phone'])
                    self.save(con)
                next_page = self.get_next_page(xhtml)
                time.sleep(self.sleep_time * 2 )
        info = '全部数据爬取结束!'
        self.logger.info(info)
        print(info)


if __name__ == '__main__':
    s = Spider_ganji()
    s.run()

