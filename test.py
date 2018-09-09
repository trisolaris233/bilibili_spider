#!C:\Users\Trisolaris\AppData\Local\Programs\Python\Python37
#-*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import json
import time
import pymysql
import logging
import sys
from wordcloud import WordCloud
import io
import matplotlib.pyplot as plt
import jieba
from os import path
import jieba.posseg as psg
import sqlite3 as sql
from queue import Queue
import threading


headers = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection':
    'keep-alive',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}

upInfoUrl = "https://api.bilibili.com/x/relation/stat"
submitUrl = "https://space.bilibili.com/ajax/member/getSubmitVideos"
danmakuUrl = "https://api.bilibili.com/x/v1/dm/list.so"
submitDetailUrl = "https://api.bilibili.com/x/web-interface/archive/stat"
archieveUrl = "https://www.bilibili.com/video/av"
databaseName = ""

total = 370000000
taskSize = 100
taskNum = int(total / taskSize)

upTasks = Queue()       # 用户任务队列
upOpts = Queue()        # 用户输出队列

submitTasks = Queue()   # 用户视频队列
submitOpts = Queue()    # 视频输出队列

danmakuTasks = Queue()  # 弹幕任务队列
danmakuOpts = Queue()   # 弹幕输出队列

# 队列的线程琐
upTasksLock = threading.Lock()
upOptsLock = threading.Lock()
submitTasksLock = threading.Lock()
submitOptsLock = threading.Lock()
danmakuTasksLock = threading.Lock()
danmakuOptsLock = threading.Lock()

upExitFlag = 0
submitExitFlag = 0
danmakuExitFlag = 0

threads = []
conn = None


# up主的信息
#   mid: up的唯一识别符
#   follower: up主的粉丝数量
class up(object):
    def __init__(self, mid=0, follower=0):
        self.mid = mid
        self.follower = follower

    def getSubmitNumber(self):
        url = "%s?mid=%s&page=1&pagesize=1" % (submitUrl, str(self.mid))
        # print(url)
        try:
            return getDict(getHTMLText(url))['data']['count']
        except:
            return -1

    # 获取该up主的投稿信息
    def getSubmit(self):
        url = "%s?mid=%s&page=1&pagesize=%s" % (submitUrl, str(self.mid), str(self.getSubmitNumber()))
        # print(url)
        submitDict = ""
        resList = []
        try:
            submitDict = getDict(getHTMLText(url))
            # print(submitDict)
            vlist = submitDict['data']['vlist']

            # 遍历每一个投稿
            for item in vlist:
                resList.append(submit(
                  item['typeid'],
                  item['play'],
                  item['title'],
                  item['created'],
                  item['video_review'],
                  item['favorites'],
                  item['aid'],
                  self.mid
                ))

        except:
            return resList
        return resList

    # 获取该up主的投稿信息
    def getSubmitEx(self):
        url = "%s?mid=%s&page=1&pagesize=%s" % (submitUrl, str(self.mid),
                                                str(self.getSubmitNumber()))
        # print(url)
        submitDict = ""
        resList = []
        try:
            text = getHTMLText(url)
            if text == "failed":
                return "failed"

            submitDict = getDict(text)
            # print(submitDict)
            vlist = submitDict['data']['vlist']

            # 遍历每一个投稿
            for item in vlist:
                aid = item['aid']
                submitDetailDict = {}
                detail = {}
                try:
                    # 取得每一个投稿的详细信息
                    url = "%s?aid=%s" % (submitDetailUrl, str(aid))
                    submitDetailDict = getDict(getHTMLText(url))
                    detail = submitDetailDict['data']
                except:
                    return []

                resList.append(
                    submitEx(
                      item['typeid'],
                      item['play'],
                      item['title'],
                      item['created'],
                      item['video_review'],
                      item['favorites'],
                      aid,
                      self.mid,
                      detail['reply'],
                      detail['coin'],
                      detail['like'],
                      detail['his_rank']
                    )
                  )

        except:
            return resList
        return resList

# 单条弹幕
#   sendtime: 发送时间
#   content: 内容
#   dtype: 弹幕类型
#   adi: 视频的AV号
class danmaku(object):
    def __init__(
      self,
      sendtime="",
      content="",
      dtype=0,
      aid=0
    ):
        self.sendtime = sendtime
        self.content = content
        self.type = dtype
        self.aid = aid


# 简易投稿信息
#   typeid: 分区id
#   play: 播放量
#   title: 标题
#   createdTime: 时间
#   numDanmaku: 弹幕数量
#   favorites: 收藏量
#   aid: AV号
class submit(object):
    def __init__(
      self,
      typeid = 0,
      play = 0,
      title = "",
      createdTime = 0,
      danmaku = 0,
      favorites = 0,
      aid = 0,
      mid = 0
      ) :
        self.typeid = typeid
        self.play = play
        self.title = title
        self.createdTime = createdTime
        self.danmaku = danmaku
        self.favorites = favorites
        self.aid = aid
        self.mid = mid

    # 获取视频oid
    def getOid(self):
        url = "%s%s" % (archieveUrl, str(self.aid))
        text = ""
        try:
            text = getHTMLText(url)
        except:
            return -1
        oidInfo = re.findall(r'"cid":[\d]*', text)
        '''
          突然发现有一些视频不知道为什么提取不了cid. 这些视频的普遍特征就是在B站看的时候预览
          显示不出播放量。 应该是早期作♂品
        '''
        try:
            return eval(oidInfo[0].split(':')[1])
        except:
            oidInfo = re.findall(r'"cid": [\d]*', text)
            try:
                return eval(oidInfo[0].split(':')[1])
            except:
                return -1

    # 获取弹幕列表
    def getDanmaku(self):
        url = "%s?oid=%s" % (danmakuUrl, str(self.getOid()))
        text = ""
        resList = []
        try:
            text = getHTMLText(url)
            if text == "failed":
                return "failed"
            soup = BeautifulSoup(text, 'lxml')
            ds = soup.find_all('d')

            # 遍历所有弹幕标签
            for item in ds:
                dproperty = item.get('p')
                dps = dproperty.split(',')
                resList.append(danmaku(
                  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(eval(dps[4]))),
                  item.get_text(),
                  eval(dps[1]),
                  self.aid
                ))

        except:
            return resList
        return resList

    # 获取评论列表
    def getReply(self):
        pass


# 详细投稿信息
# 增加的字段:
#   reply: 回复数量
#   coin: 投币数量
#   like: 推荐数量
#   rank: 历史最高排名
class submitEx(submit):
    def __init__(
      self,
      typeid = 0,
      play = 0,
      title = "",
      createdTime = 0,
      danmaku = 0,
      favorites = 0,
      aid = 0,
      mid = 0,
      reply = 0,
      coin = 0,
      like = 0,
      rank = 0
    ):
        super(submitEx, self).__init__(
          typeid,
          play,
          title,
          createdTime,
          danmaku,
          favorites,
          aid,
          mid
        )
        self.reply = reply
        self.coin = coin
        self.like = like
        self.rank = rank


class spThread (threading.Thread):
    def __init__(self, pfun, *para):
        threading.Thread.__init__(self)
        self.pfun = pfun
        self.para = para

    def run(self):
        try:
            self.pfun(self.para)
        except:
            pass

# 判断合法的up
def checkVaildUp(upInfo):
    if upInfo.follower >= 30000:
        return True
    return False

# 获取html页面
def getHTMLText(url):
    try:
        r = requests.get(url, headers=headers, timeout=3)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "failed"


# 将字符串转为字典
def getDict(text):
    try:
        return json.loads(text)
    except:
        return ""


# 根据mid取得up主对象
def getUp(mid):
    url = "%s?vmid=%s" % (upInfoUrl, str(mid))
    text = getHTMLText(url)
    if text == "failed":
        return "failed"
    try:
        updict = getDict(text)
        return up(updict['data']['mid'], updict['data']['follower'])
    except:
        return ""


def printObj(obj):
    print(obj.__dict__)

# 生成哲♂学字典
# 实测没啥卵用
def makePhilosophyDict():
    f = open(
        "dict.txt",
        'r',
        encoding = 'UTF-8'
    ).read()
    f2 = open("dic♂t.txt", 'w', encoding='utf-8')
    # 使用集合来避免重复
    s = set()
    for item in jieba.cut(f, cut_all=True):
        for i in range(0, len(item)):
            s.add("%s♂%s" % (item[0:i], item[i: len(item)]))
        s.add("%s♂" % (item))

    for item in s:
        f2.write(item)
        f2.write("\n")

# 测试用的程序
# 画一个云图
def drawWordCloud():
    text = open('danmaku.txt', 'r', encoding='UTF-8').read()
    cut_text = ",".join(jieba.cut(text))
    print(cut_text)

    wordcloud = WordCloud(
        #设置字体，不然会出现口字乱码，文字的路径是电脑的字体一般路径，可以换成别的
        font_path="msyh.ttf",
        #设置了背景，宽高
        background_color="white",
        width=1500,
        height=960).generate(cut_text)

    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('ciyun.png')
    plt.show()
    print("complete")

# 获取Up主基本信息线程
def getUpTaskThread(id):
    global upExitFlag
    while not upExitFlag:
        # 取得琐
        upTasksLock.acquire()
        if not upTasks.empty():
            # 从队列中取出数据
            data = upTasks.get()
            # 释放锁
            upTasksLock.release()
            print("thread No.%s has carried task %s\n" % (str(id[0]), str(data)))

            i = data * taskSize + 1
            endi = (data + 1) * taskSize + 1

            while i < endi:
                upInfo = getUp(i)
                # 如果没有被屏蔽
                if upInfo != "failed":
                    # 检查up是否合法
                    if checkVaildUp(upInfo):
                        # 将得到的用户信息推入用户输出队列
                        upOptsLock.acquire()
                        upOpts.put(upInfo)
                        upOptsLock.release()

                        # 将取到的用户插入视频任务队列 爬取视频
                        submitTasksLock.acquire()
                        submitTasks.put(upInfo)
                        submitTasksLock.release()
                    i = i + 1
                # 被屏蔽就持续循环
            print("thread No.%s has finished task %s\n" % (str(id[0]), str(data)))
        else:
            upTasksLock.release()
        # 歇会儿吧您呐!
        time.sleep(1)

def getUpOptThread(id):
    while not upExitFlag:
        upOptsLock.acquire()
        if not upOpts.empty():
            tmp = upOpts.get()
            upOptsLock.release()
            s = "INSERT INTO upInfo(mid, follower) VALUES('%d', '%d')" % (
                tmp.mid, tmp.follower)
            cursor = conn.cursor()
            cursor.execute(s)
            conn.commit()
            print("make a record")
        else:
            upOptsLock.release()

def getSubmitThread(id):
    while not submitExitFlag:
        submitTasksLock.acquire()
        if not submitTasks.empty():
            # 取得用户
            upInfo = submitTasks.get()
            submitTasksLock.release()

            print("thread No.%d has gained user %d's submits.\n" % (id[0], upInfo.mid))
            # 取得视频
            submitInfo = upInfo.getSubmitEx()

            # 爬取失败， 循环爬取
            while submitInfo == "failed":
                print("failed to get submits.\n")
                submitInfo = upInfo.getSubmitEx()

            # 没有上传视频或者获取失败
            if submitInfo != []:
                # 将得到的视频信息压入视频输出队列
                submitOptsLock.acquire()
                submitOpts.put(submitInfo)
                submitOptsLock.release()

                # 弹幕任务队列上锁
                danmakuTasksLock.acquire()
                # 将视频信息推入弹幕任务队列
                danmakuTasks.put(submitInfo)
                danmakuTasksLock.release()

        else:
            submitTasksLock.release()

        time.sleep(1)
    pass

def getSubmitOptThread(id):
    while not submitExitFlag:
        submitOptsLock.acquire()
        if not submitOpts.empty():
            submits = submitOpts.get()
            submitOptsLock.release()

            for i in submits:
                s = '''
                    INSERT INTO submit(
                        typeid,
                        play,
                        title,
                        createTime,
                        danmaku,
                        favorites,
                        aid,
                        reply,
                        coin,
                        likes,
                        rank
                    ) VALUES(
                        '%d', '%d', '%s', '%s', '%d',
                        '%d', '%d', '%d', '%d', '%d',
                        '%d' );
                ''' % (
                    i.typeid,
                    i.play,
                    i.title,
                    i.createTime,
                    i.danmaku,
                    i.favorites,
                    i.aid,
                    i.reply,
                    i.coin,
                    i.like,
                    i.rank
                )
                cursor = conn.cursor()
                cursor.execute(s)
                conn.commit()
        else:
            submitOptsLock.release()

def getDanmakuThread(id):
    while not danmakuExitFlag:
        danmakuTasksLock.acquire()
        if not danmakuTasks.empty():
            archieves = danmakuTasks.get()
            danmakuTasksLock.release()

            # 遍历每个视频
            for i in archieves:

                d = i.getDanmaku()
                print(
                    "thread No.%d has gained danmaku of av%d" % (id[0], i.aid))
                # ip被封锁， 循环获取
                while d == "failed":
                    print("failed to get danmaku")
                    d = i.getDanmaku()

                if d != []:
                    # 将得到的弹幕压入弹幕输出队列
                    danmakuOptsLock.acquire()
                    danmakuOpts.put(d)
                    danmakuOptsLock.release()

        else:
            danmakuTasksLock.release()
        time.sleep(1)



def getDanmakuOptThread(id):
    while not danmakuExitFlag:
        danmakuOptsLock.acquire()
        if not danmakuOpts.empty():
            d = danmakuOpts.get()
            danmakuOptsLock.release()


            # 遍历所有弹幕
            for i in d:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                        INSERT INTO danmaku(
                            sendtime,
                            content,
                            dtype,
                            aid
                        ) VALUES(?,?,?,?);
                    ''',
                    (i.sendtime, i.content, i.dtype, i.aid)
                )
                conn.commit()
        else:
            danmakuOptsLock.release()


def init():
    global conn
    print("init database...")
    databaseName = input("input your database name: ")
    databasePath = "%s.db" % (databaseName)

    while path.exists(databasePath):
        print("invalid database name. please enter a filename that does not exist")
        databaseName = input("input your database name: ")
        databasePath = "%s.db" % (databaseName)

    # 链接数据库
    conn = sql.connect(databasePath)

    # 创建数据表
    callList = []
    callList.append(createUpInfoTable)
    callList.append(createSubmitTable)
    callList.append(createDanmakuTable)
    promptList = ["upInfo", "submit", "danmaku"]
    i = 0

    for item in promptList:
        print("creating table '%s'" % (item))
        if callList[i]():
            print("creating table '%s' successfully" % (item))
        else:
            print("failed to create table '%s'" % (item))
            input("press any key to exit...")
            quit()
        i = i + 1


    print("init database successfully")


def createUpInfoTable():
    try:
        s = '''CREATE TABLE upInfo(
        mid INT UNSIGNED NOT NULL,
        follower INT UNSIGNED NOT NULL
        );'''
        cursor = conn.cursor()
        cursor.execute(s)
        cursor.close()
        conn.commit()
    except:
        return False
    return True

def createSubmitTable():
    try:
        s = '''
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
        cursor = conn.cursor()
        cursor.execute(s)
        cursor.close()
        conn.commit()
    except:
        return False
    return True

def createDanmakuTable():
    try:
        s = '''
            CREATE TABLE danmaku(
                sendtime DATETIME NOT NULL,
                content TEXT NOT NULL,
                dtype INT UNSIGNED NOT NULL,
                aid INT UNSIGNED NOT NULL
            );
        '''
        cursor = conn.cursor()
        cursor.execute(s)
        cursor.close()
        conn.commit()
    except:
        return False
    return True



if __name__ == "__main__":
    init()
    threadid = 0

    print("loading tasks...")
    # 遍历所有用户
    # 如果要遍历全部用户 将37000替换成 taskNum.
    # 仅供测试用
    for i in range(0, 37000):
        upTasks.put(i)
    print("loading tasks successfully")

    # 开启n条线程爬用户基本数据
    # 三条线程就炸了， 2条差不多..
    # 代理IP是必需品呀！！
    for i in range(0, 2):
        thread = spThread(getUpTaskThread, threadid)
        thread.start()
        threads.append(thread)
        threadid = threadid + 1

    # 再开启n条线程爬取视频信息
    for i in range(0, 2):
        thread = spThread(getSubmitThread, threadid)
        thread.start()
        threads.append(thread)
        threadid = threadid + 1

    # 开启n条线程爬取弹幕
    for i in range(0, 2):
        thread = spThread(getDanmakuThread, threadid)
        thread.start()
        threads.append(thread)
        threadid = threadid + 1


    while not upTasks.empty() or not submitTasks.empty() or not danmakuTasks.empty():
        upOptsLock.acquire()
        if not upOpts.empty():
            tmp = upOpts.get()
            upOptsLock.release()
            s = "INSERT INTO upInfo(mid, follower) VALUES('%d', '%d')" % (
                tmp.mid, tmp.follower)
            cursor = conn.cursor()
            cursor.execute(s)
            conn.commit()
        else:
            upOptsLock.release()
        submitOptsLock.acquire()

        if not submitOpts.empty():
            submits = submitOpts.get()
            submitOptsLock.release()

            # 遍历所有投稿
            for i in submits:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO submit(
                        typeid,
                        play,
                        title,
                        createTime,
                        danmaku,
                        favorites,
                        aid,
                        reply,
                        coin,
                        likes,
                        rank,
                        upmid
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?);''',
                    (i.typeid, i.play, i.title, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i.createdTime)),
                     i.danmaku, i.favorites, i.aid, i.reply, i.coin, i.like,
                     i.rank, i.mid))
                conn.commit()
        else:
            submitOptsLock.release()

        danmakuOptsLock.acquire()
        if not danmakuOpts.empty():
            d = danmakuOpts.get()
            danmakuOptsLock.release()

            # 遍历所有弹幕
            for i in d:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                        INSERT INTO danmaku(
                            sendtime,
                            content,
                            dtype,
                            aid
                        ) VALUES(?,?,?,?);
                    ''', (i.sendtime, i.content, i.type, i.aid))
                conn.commit()
        else:
            danmakuOptsLock.release()


    upExitFlag = 1

    for i in threads:
        i.join()
