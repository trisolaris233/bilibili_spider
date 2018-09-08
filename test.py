# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import json



# up主的信息
#   mid: up的唯一识别符
#   follower: up主的粉丝数量
class up(object):
    def __init__(self, mid=0, follwer=0):
        self.mid = mid
        self.follwer = follwer

    # 获取该up主的投稿信息
    def getSubimtInfo(self):
      pass

    # 获取该up主的投稿详情
    def getSubmitInfoEx(self):
      pass

# 单条弹幕
#   sendtime: 发送时间
#   content: 内容
#   dtype: 弹幕类型
class danmakuInfo(object):
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

    # 获取弹幕列表
    def getDanmaku(self):
      pass

    # 获取评论列表
    def getReply(self):
      pass


# 详细投稿信息
# 增加的字段:
#   reply: 回复数量
#   coin: 投币数量
#   like: 推荐数量
#   rank: 历史最高排名
class submitEx(submitInfo):
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
upSubmitUrl = "https://space.bilibili.com/ajax/member/getSubmitVideos"
danmakuUrl = "https://api.bilibili.com/x/v1/dm/list.so"
videoUrl = "https://api.bilibili.com/x/web-interface/archive/stat"


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
  pass




