import bilibili
import re
from bs4 import BeautifulSoup
import danmaku
import time
import bException
import reply
import datetime

# 简易投稿信息
#   typeid: 分区id
#   play: 播放量
#   title: 标题
#   createdTime: 时间
#   numDanmaku: 弹幕数量
#   favorites: 收藏量
#   aid: AV号
class submit(object):
    def __init__(self,
                 typeid=0,
                 play=0,
                 title="",
                 createdTime=0,
                 danmaku=0,
                 favorites=0,
                 aid=0,
                 mid=0):
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
        url = "%s%s" % (bilibili.archieveUrl, str(self.aid))
        text = ""
        try:
            text = bilibili.getHTMLText(url)
        except bException.bError as e:
            raise e
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

    def __getDanmakuHelper(self, text):
        resList = []
        soup = BeautifulSoup(text, 'lxml')
        ds = soup.find_all('d')

        # 遍历所有弹幕标签
        for item in ds:
            dproperty = item.get('p')
            dps = dproperty.split(',')
            resList.append(
                danmaku.danmaku(
                    time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(eval(dps[4]))),
                    item.get_text(), eval(dps[1]), self.aid))
        return resList

    # 获取历史弹幕
    # date: datetime对象
    def getHistoryDanmaku(self, date):
        url = "%s?type=1&date=%s&oid=%d" % (
            bilibili.historyDanmakuUrl,
            date.strftime("%Y-%m-%d"),
            self.getOid()
        )
        print(url)

        try:
            return self.__getDanmakuHelper(bilibili.getHTMLText(url, bilibili.login_headers))
        except bException.bError as e:
            raise e

    # 获取所有历史弹幕, 另存为文件
    def getAllDanmakus(self, path):
        # 获取当前时间
        today = datetime.datetime.now()
        # 获取视频发布时间
        createdDate = datetime.datetime.fromtimestamp(self.createdTime)
        # 获取两日间隔
        daysGap = today - createdDate

        fileobj = open(path, 'w', encoding="UTF-8")
        # 写入文件头
        fileobj.write('''
        <?xml version="1.0" encoding="UTF-8"?><i>
        <chatserver>chat.bilibili.com</chatserver>
        <mission>0</mission>
        <maxlimit>%d</maxlimit>
        <state>0</state>
        <real_name>0</real_name>
        <source>k-v</source>
        ''' % (self.danmaku))
        #循环每一天
        for i in range(0, daysGap.days):
            date = createdDate + datetime.timedelta(days=i)
            # 请求地址
            url = "%s?type=1&date=%s&oid=%d" % (
                bilibili.historyDanmakuUrl,
                date.strftime("%Y-%m-%d"),
                self.getOid()
            )
            text = ""
            print("getting %s\n" % (url))
            try:
                text = bilibili.getHTMLText(url, bilibili.login_headers)
            except :
                continue

            soup = BeautifulSoup(text, 'lxml')
            ds = soup.find_all('d')
            s = set()
            for i in ds:
                s.add(str(i))
            for i in s:
                fileobj.write(i)


        fileobj.write("</i>")
        fileobj.close()


    # 获取弹幕列表
    def getDanmaku(self):
        url = "%s?oid=%s" % (bilibili.danmakuUrl, str(self.getOid()))
        text = ""
        # resList = []
        try:
            text = bilibili.getHTMLText(url)
            # soup = BeautifulSoup(text, 'lxml')
            # ds = soup.find_all('d')

            # # 遍历所有弹幕标签
            # for item in ds:
            #     dproperty = item.get('p')
            #     dps = dproperty.split(',')
            #     resList.append(
            #         danmaku.danmaku(
            #             time.strftime("%Y-%m-%d %H:%M:%S",
            #                           time.localtime(eval(dps[4]))),
            #             item.get_text(), eval(dps[1]), self.aid))
            return self.__getDanmakuHelper(text)

        except bException.bError as e:
            raise e
        return resList

    # 获取评论信息, 比如评论的数量， 评论的用户数
    def getReplyInfo(self):
        try:
            url = "%s?pn=%d&type=%d&oid=%d&sort=%d" % (
                bilibili.replyUrl,
                1,
                1,
                self.getOid(),
                1
            )
            res = bilibili.getDict(bilibili.getHTMLText(url))

            resDict = {}
            resDict['acount'] = res['data']['page']['acount']
            resDict['count'] = res['data']['page']['count']
        except bException.bError as e:
            raise e

    # 获取评论数量
    def getReplyNum(self):
        try:
            return self.getReplyInfo()['acount']
        except bException.bError as e:
            raise e

    # 获取评论辅助方法
    # 只获取一级评论
    def __getReplyHelper(self, replyDict):
        repliesList = []
        if replyDict == None:
            return repliesList
        for r in replyDict:
            nr = reply.reply(
                    r['content']['message'],
                    r['member']['mid'],
                    r['member']['uname'],
                    r['floor'],
                    r['ctime'],
                    r['like'],
                    r['content']['plat'],
                    r['oid'],
                    r['rpid'],
                    r['root'],
                    self.mid
                )
            repliesList.append(nr)

        return repliesList

    # 获取评论列表
    def getReply(self, page = 1, sort = 1):
        try:
            url = "%s?pn=%d&type=%d&oid=%d&sort=%d" % (
                bilibili.replyUrl,
                page,
                1,
                self.aid,
                sort
            )
            # print(url)
            res = bilibili.getDict(bilibili.getHTMLText(url))

            return self.__getReplyHelper(res['data']['replies'])

        except bException.bError as e:
            raise e


# 详细投稿信息
# 增加的字段:
#   reply: 回复数量
#   coin: 投币数量
#   like: 推荐数量
#   rank: 历史最高排名
class submitEx(submit):

    def __init__(self,
                 typeid=0,
                 play=0,
                 title="",
                 createdTime=0,
                 danmaku=0,
                 favorites=0,
                 aid=0,
                 mid=0,
                 reply=0,
                 coin=0,
                 like=0,
                 rank=0):
        super(submitEx, self).__init__(typeid, play, title, createdTime,
                                       danmaku, favorites, aid, mid)
        self.reply = reply
        self.coin = coin
        self.like = like
        self.rank = rank
