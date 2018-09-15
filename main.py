#-*- coding: utf-8 -*-

import b
import time
import json
import datetime
import spider
import localDb
from queue import Queue
import threading
import proxy
import config


upperInfoTableName = "upper"
submitInfoTableName = "submit"
danmakuInfoTableName = "danmaku"
repliesInfoTableName = "reply"

sqlCreateUpperInfo = '''
    CREATE TABLE upper(
        mid INT UNSIGNED NOT NULL,
        follower INT UNSIGNED NOT NULL,
        uname TEXT NOT NULL,
        face TEXT NOT NULL,
        regtime INT UNSIGNED NOT NULL,
        sex TEXT NOT NULL,
        level INT UNSIGNED NOT NULL,
        vipType INT UNSIGNED NOT NULL,
        vipStatus INT UNSIGNED NOT NULL
        );
'''
sqlCreateSubmitInfo = '''
CREATE TABLE submit(
                typeid INT UNSIGNED NOT NULL,
                play INT UNSIGNED NOT NULL,
                title TEXT NOT NULL,
                createTime DATETIME NOT NULL,
                danmaku INT UNSIGNED NOT NULL,
                favorites INT UNSIGNED NOT NULL,
                aid INT UNSIGNED NOT NULL,
                reply INT UNSIGNED NOT NULL,
                coin INT UNSIGNED NOT NULL,
                likes INT UNSIGNED NOT NULL,
                rank INT UNSIGNED NOT NULL,
                upmid INT UNSIGNED NOT NULL
            );
'''
sqlCreateDanmakuInfo = '''
            CREATE TABLE danmaku(
                sendtime DATETIME NOT NULL,
                content TEXT NOT NULL,
                dtype INT UNSIGNED NOT NULL,
                aid INT UNSIGNED NOT NULL
            );
        '''
sqlCreateRepliesInfo = '''
    CREATE TABLE reply(
        content TEXT NOT NULL,
        senderID INT UNSIGNED NOT NULL,
        senderName TEXT NOT NULL,
        floor INT UNSIGNED NOT NULL,
        sendTime DATETIME NOT NULL,
        likes INT UNSIGNED NOT NULL,
        subReplies INT UNSIGNED NOT NULL,
        aid INT UNSIGNED NOT NULL,
        rid INT UNSIGNED NOT NULL,
        fid INT UNSIGNED NOT NULL,
        upmid INT UNSIGNED NOT NULL
    );
'''
sqlInsertUpperInfo = '''
    INSERT INTO upper(
        mid,
        follower,
        uname,
        face,
        regtime,
        sex,
        level,
        vipType,
        vipStatus
    ) VALUES(?,?,?,?,?,?,?,?,?);
'''

tableList = [
    upperInfoTableName,
    submitInfoTableName,
    danmakuInfoTableName,
    repliesInfoTableName
]

createTableSqlList = [
    sqlCreateUpperInfo,
    sqlCreateSubmitInfo,
    sqlCreateDanmakuInfo,
    sqlCreateRepliesInfo
]

class task:
    def __init__(self):
        self.queue = Queue()
        self.mutex = threading.Lock()


    def get(self):
        self.mutex.acquire()
        res = self.queue.get()
        self.mutex.release()
        return res

    def put(self, arg):
        self.mutex.acquire()
        self.queue.put(arg)
        self.mutex.release()

    def empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()

total = 370000000
taskSize = 100
taskNum = int(total / taskSize)

# 任务对象
upperInputTask = task()     # up主输入队列
upperOutputTask = task()    # up主输出队列
SubmitInputTask = task()    # 视频输入队列
submitOutputTask = task()   # 视频输出队列
dbLock = threading.Lock()
proxiesPool = proxy.proxyPool()
cfg = config.config("config.json")
db = None

def isNum(s):
    try:
        int(s)
    except:
        return False
    return True


# 初始化， 任务和数据库等
def init():
    global cfg
    # 读取配置文件
    global db
    # 初始化任务
    for i in range(1, 1001):
        upperInputTask.put(i)

    # 初始化数据库， 没有数据表则创建之
    db = localDb.localDb(cfg.getAttr('dbpath'))
    index = 0
    for eachTable in tableList:
        if not db.isTableExists(eachTable):
            db.execute(createTableSqlList[index])
        index = index + 1



def crawlUppers(tupleArg, dictArg):
    threadid = tupleArg[0]
    carry = dictArg['carry']
    output = dictArg['output']
    cfg = dictArg['cfg']
    pool = dictArg['pool']
    proxies = {}
    p = None

    # 循环直到任务队列为空
    while not carry.empty():
        # 取走一个任务, 取得其任务编号
        taskNum = carry.get()

        print("thread%d has carried %d\n" % (threadid, taskNum))

        # 每个任务编号相当于taskSize个小任务
        for i in range(1, taskSize + 1):
            tinyNum = (taskNum - 1) * taskSize + i  # 任务编号是从1开始编的
            try:
                upper = b.getUpper(tinyNum, cfg, proxies) # 获取用户
            except:
                continue
            # print("work on %d\n" % (tinyNum))

            if upper == None:
                continue

            if isNum(upper):  # 如果是数字
                if upper != 403:
                    continue

                while upper == 403: # 如果结果为403，则更换代理ip， 循环获取
                    pool.remove(p)
                    p = pool.get()
                    while p == None:
                        p = pool.get()
                    print("proxy changed %s->%s" %
                          (proxy.castToStringIp(proxies),
                           proxy.castToStringIp(p)))
                    proxies = { "http" : proxy.castToStringIp(p) }
                    try:
                        upper = b.getUpper(tinyNum, cfg, proxies)
                    except:
                        break
            if upper != None and not isNum(upper):
                output.put(upper)  # 压入输出队列

        print("thread%d has finished %d\n" % (threadid, taskNum))

        time.sleep(1)

# 获得代理ip的线程
def updateProxiesPool(tupleArg, dictArg):
    threadid = tupleArg[0]
    exitFlag = dictArg['exitFlag']
    pool = dictArg['pool']
    # 3分钟获取一次代理ip池
    while not exitFlag:
        print("pool updated.")
        pool.update()
        time.sleep(3 * 60)


def main():
    init()

    spiders = []
    threadid = 2
    exitFlag = 0


    proxiesPool.update()            # 先获取代理ip

    proxyThread = spider.spider(    # 开启代理ip线程
        updateProxiesPool,
        1, exitFlag=exitFlag, pool=proxiesPool
    )
    proxyThread.start()
    spiders.append(proxyThread)

    for i in range(0, 30):          # 开启获取用户线程
        sp = spider.spider(
            crawlUppers,
            threadid, carry=upperInputTask, output=upperOutputTask, cfg=cfg, pool=proxiesPool
        )
        sp.start()
        spiders.append(sp)
        threadid = threadid + 1

    # 主线程， 插入数据库
    while not upperInputTask.empty() or not upperOutputTask.empty():
        if not upperOutputTask.empty():
            upper = upperOutputTask.get()
            db.execute(
                sqlInsertUpperInfo,
                (
                    upper.mid,
                    upper.follower,
                    upper.uname,
                    upper.face,
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(upper.regtime)),
                    upper.sex,
                    upper.level,
                    upper.vipType,
                    upper.vipStatus
                )
            )
    exitFlag = 1

    for i in spiders:
        i.join()

if __name__ == "__main__":
    main()