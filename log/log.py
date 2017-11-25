import logging
import time

class Logger(object):
    def __init__(self,file_name,name):
        logging.basicConfig(
            level=logging.INFO,
            filename= file_name,
            filemode='a'
        )

        self.logger = logging.getLogger(name)
    def info(self,msg):
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()- 8*60*60 ))
        self.logger.info(str(cur_time)+':'+str(msg))
    def error(self,msg):
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()-8*60*60))
        self.logger.error(str(cur_time) + ':' + str(msg) )

