import bilibili
import re
from bs4 import BeautifulSoup
import danmaku
import time

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
        url = "%s?oid=%s" % (bilibili.danmakuUrl, str(self.getOid()))
        text = ""
        resList = []
        try:
            text = bilibili.getHTMLText(url)
            if text == "failed":
                return "failed"
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

        except:
            return resList
        return resList

    # 获取评论列表
    def getReply(self):
        pass
