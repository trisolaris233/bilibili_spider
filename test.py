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


class mysql(object):
    def __init__(
      self,
      host="localhost",
      user="root",
      pwd="",
      db=""
    ):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = None
        self.cur = None

    #链接数据库
    def connect(self):
        try:
            self.conn = pymysql.connect(
                self.host, self.user, self.pwd, self.db, charset='utf8')
        except:
            return False
        self.cur = self.conn.cursor()
        return True

    def execute(self, sql, params=None):
        self.connect()
        try:
            if self.conn and self.cur:
                self.cur.execute(sql, params)
                self.conn.commit()
        except:
            self.conn.close()
            return False
        return True

    def fetchall(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchall()


# up主的信息
#   mid: up的唯一识别符
#   follower: up主的粉丝数量
class up(object):
    def __init__(self, mid=0, follwer=0):
        self.mid = mid
        self.follwer = follwer

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
                  item['aid']
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
            submitDict = getDict(getHTMLText(url))
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
class danmaku(object):
    def __init__(
      self,
      sendtime="",
      content="",
      dtype=0
    ):
        self.sendtime = sendtime
        self.content = content
        self.type = dtype


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
      aid = 0
      ) :
        self.typeid = typeid
        self.play = play
        self.title = title
        self.createdTime = createdTime
        self.danmaku = danmaku
        self.favorites = favorites
        self.aid = aid

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
            soup = BeautifulSoup(text, 'lxml')
            ds = soup.find_all('d')

            # 遍历所有弹幕标签
            for item in ds:
                dproperty = item.get('p')
                dps = dproperty.split(',')
                resList.append(danmaku(
                  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(eval(dps[4]))),
                  item.get_text(),
                  eval(dps[1])
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
          aid
        )
        self.reply = reply
        self.coin = coin
        self.like = like
        self.rank = rank

# 获取html页面
def getHTMLText(url):
    try:
        r = requests.get(url, headers=headers, timeout=3)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""


# 将字符串转为字典
def getDict(text):
    return json.loads(text)


# 根据mid取得up主对象
def getUp(mid):
    url = "%s?vmid=%s" % (upInfoUrl, str(mid))
    updict = getDict(getHTMLText(url))

    try:
        return up(updict['data']['mid'], updict['data']['follower'])
    except:
        return ""


def printObj(obj):
    print(obj.__dict__)


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
    plt.savefig('ciyun3.png')
    plt.show()
    print("complete")


if __name__ == "__main__":
