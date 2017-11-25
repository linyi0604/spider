#coding:utf8
from log import log
import settings
import random
import re
import time
import requests
from lxml import etree
from data_base.save import *

'''
抓取58同城网站上 北京地区的租房信息里 各个中介信息 中介代理人信息
'''

class Spider_58(object):
    def __init__(self):
        self.start_url = 'http://bj.58.com/zufang/pn1/'
        self.logger = log.Logger(file_name='log/58.log',name='58同城爬虫')
        self.sleep_time = settings.sleep_time # 防止反爬 休息后继续的时间
        self.retry_time = settings.RETRY_TIME # 访问失败 重复访问次数
        self.headers = settings.HEADERS
        self.total = 0

        # 代理ip对象
        # self.proxy = proxies.MyProxies()
        # self.cur_ip = self.proxy.get_ip()



    def parse_url(self,url,proxy = None):
        '''发送请求
            拿到etree转化后的html
        '''
        # proxy = self.cur_ip
        random_time = random.randint(self.sleep_time//2,self.sleep_time*2)
        time.sleep(random_time)
        self.logger.info("正在获取链接：%s"%url)
        try :

            header = random.choice(self.headers)
            response = requests.get(url=url,headers=header,proxies=proxy,timeout=10)
            # 如果获取的状态码 不是200  那么就抛出异常 重新爬
            assert response.status_code == 200
            self.logger.info("成功获取链接：" + url)
            xhtml =  etree.HTML(response.content)

            # 检验是否被反爬
            check = xhtml.xpath('//input[@value="点击按钮进行验证"]')
            if check:
                self.logger.info('当前被反爬,需要人为干预!')
                print('当前被反爬,需要人为干预!')
                self.wait(url) # 人为干预
                response = self.parse_url(url)
                xhtml = etree.HTML(response.content)

            self.retry_time = settings.RETRY_TIME
            return xhtml

        except Exception as e :
            print(e)
            self.logger.error(str(e))
            if self.retry_time > 0:
                self.logger.error('发送请求发生异常,更换ip再次尝试,请求地址:%s' % url)
                self.logger.error(str(e))
                self.retry_time -= 1
                self.parse_url(url)
            else :
                self.retry_time = settings.RETRY_TIME
                self.logger.error('尝试'+str(settings.RETRY_TIME)+'次请求仍然失败,请求地址:%s'%url)
                self.logger.error('错误信息:'+str(e))
                return None
            # self.logger.info('代理ip无法使用,更换代理ip!')
            # self.cur_ip = self.proxy.get_ip()
            # self.logger.info('成功获取代理ip:'+str(self.cur_ip))
            return self.parse_url(url)

    def get_next_page(self,xhtml):
        '''获取下一页的链接 如果没有下一页 返回None'''
        try:
            self.logger.info('尝试获取下一页')
            next_page = xhtml.xpath('//a[@class="next"]/@href')
            next_page=next_page[0] if next_page else None
            self.logger.info('成功获取下一页链接:'+next_page)
            return next_page
        except Exception as e :
            print('全部数据爬取完成,爬虫结束!')
            self.logger.info('全部数据爬取完成,爬虫结束!')
            return None

    def get_content_xhtml_list(self,xhtml):
        '''获取主页面下所有content的基本信息'''
        li_list = xhtml.xpath('//ul[@class="listUl"]/li')
        content_list = []
        for li in li_list:
            content = {}
            # 信息来源
            source = li.xpath('.//div[@class="jjr"]/text()')
            # 如果是个人的 就不抓取
            if not source:
                continue
            # 该条信息的链接
            href = li.xpath('.//div[@class="des"]/h2/a/@href')
            content['href'] = href[0] if href else None
            # 该条信息发布人姓名
            name = li.xpath('.//span[@class="listjjr"]/a/text()')
            content['name'] = name[0] if name else None
            # 该条信息的中介名称 和 门店名称
            agency = li.xpath('.//span[@class="jjr_par_dp"]/text()')
            agency = agency[0] if agency else None
            if agency is not None:
                agency = re.sub(r'\r\n','',agency)
                agency = re.sub(r'\s+','',agency)
                # 中介名称
                content['agency_name'] = agency.split('-')[0]
                # 中介门店名称
                content['store_name'] = agency.split('-')[-1] if len(agency.split('-'))>1 else '无'
            content_list.append(content)
        return content_list

    def get_detail_list(self,con):
        '''根据基本信息 进入每一项获取更详细的信息'''
        xhtml = self.parse_url(con['href'])
        if xhtml is None:
            self.logger.info('本条抓取失败,网络状态不好或被反爬,或尝试认为干预,本条忽略,继续向下')
            self.wait(con['href'])
            return
        # 获取头像
        head_pic =  xhtml.xpath('//div[contains(@class,"agent-head-portrait")]//img/@src')
        head_pic = head_pic[0] if head_pic else None
        con['head_picture_href']=head_pic
        # 获取电话号码
        phone = xhtml.xpath('//span[@class="house-chat-txt"]/text()')
        phone = phone[0] if phone else None
        con['phone'] = phone

        # 获取经纪人服务小区列表
        dept_list = xhtml.xpath('//div[contains(@class,"agent-service-district")]/p/a/text()')
        con['dept_list'] = dept_list
        # 获取该经纪人的个人链接
        detail_url = xhtml.xpath('//p[contains(@class,"agent-name")]/a/@href')
        detail_url = detail_url[0] if detail_url else None
        con['detail_url'] = detail_url

    def wait(self,url):
        '''发生反爬 人为干预'''
        info = '请尝试人为解决反爬问题,登陆网站输入验证码: ' + str(url)
        self.logger.info(info)
        print(info)
        input('人为干预输入验证码后,回车继续!!!!!!!')

    def get_into_person_page(self,con):
        '''进入经纪人的主页,获取公司的更多信息'''
        if con['detail_url'] is None:
            return

        xhtml = self.parse_url(con['detail_url'])

        # 获取经纪人的更多信息
        lis = xhtml.xpath('//div[@class="mod-box"]/ul/li')

        detail = []
        for li in lis:
            text = li.xpath(".//text()")
            r = []
            for t in text:
                t=re.sub(r'\s+','',t)
                t=t.rstrip('：')
                if r != "":
                    r.append(t)
            for i in range(len(r)-1,-1,-1):
                if r[i] == "" :
                    r.remove(r[i])
            detail.append(r)
            for t in detail:
                if len(t)>1 and t[0]=="服务区域":
                    con['area']  = t[1]


    def save(self,con):
        '''对数据进行保存'''
        try:
            info = save(con)
            self.total += 1
            self.logger.info('已成功获取数据数量:'+ str(self.total) )
            self.logger.info(info)
        except Exception as e:
            # print(e)
            self.logger.info('存储数据发生错误:'+str(e))


    def run(self):
        self.logger.info('-' * 20 + "进入run")
        next_page = self.start_url
        # 循环爬取下一页
        while next_page is not None:
            xhtml = self.parse_url(next_page) # 主列表页面的页面xhtml
            # 获取主列表页面上每一项的信息
            content_list = self.get_content_xhtml_list(xhtml)
            self.logger.info(str(content_list))
            for con in content_list:
                self.logger.info('-' * 20 + "循环抓列表")
                # 进入列表项获取更详细的信息
                self.get_detail_list(con)
                # 进入经纪人的主页 获取更详细信息
                self.get_into_person_page(con)

                # 获取的本条信息 进行保存
                print('58同城:',con['name'],con['phone'],con['dept_list'])
                self.save(con)
            # 获取下一页url
            next_page = self.get_next_page(xhtml)
            # 防止反爬 休息
            # time.sleep(self.sleep_time)
        info = '全部数据获取结束,程序退出!'
        self.logger.info(info)




if __name__ == '__main__':
    spider = Spider_58()
    try:
        spider.run()
    except Exception as e:
        print(e)
        spider.logger.error(str(e) )