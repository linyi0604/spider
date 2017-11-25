#保存功能模块复用
import pymongo
import settings
'''
主机 127.0.0.1
端口 27017
集合名称 agency
文档名称 employee

首批数据存入 db.e
重复数据存入 db.e2
'''
def save(con):
    try:
        # 1 链接对象
        client = pymongo.MongoClient(host=settings.HOST,port=settings.PORT)
        # 2 数据库名称
        db = client.agency
        # 插入数据之前先查询 是否重复
        res = db.e.find_one({'name':con["name"],'phone':con['phone']})
        if res is not None:
            info = '数据重复,存入e2文档中'
            db.e2.insert_one(con)
            return info
        else :
            info = '存入数据库成功!'
            # 3 插入数据
            db.e.insert_one(con)
            return info
    except Exception as e:
        raise e

