

# 发起链接 间隔的时间, 如果反爬严重,适当加大时间 单位是秒
sleep_time = 5
# 当请求链接失败 重试次数,可适当改变
RETRY_TIME = 10



# mongodb 的配置
HOST = '127.0.0.1'  # ip
PORT = 27017    # 端口



# 发送请求的报文头列表
HEADERS = [
    {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"},
    {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13"},
    {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13 "},
    {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3"},
    {"User-Agent":"Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50"},
]