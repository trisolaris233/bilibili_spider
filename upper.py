import bilibili

# up主的信息
#   mid: up的唯一识别符
#   follower: up主的粉丝数量
#   uname: 用户名
#   face: 头像地址
#   regtime: 注册时间戳
#   sex: 性别
#   level: 等级
#   vipType: vip类型
#   vipStatus: vip状态
class up(object):

    def __init__(
      self,
      mid=0,
      follower=None,
      uname=None,
      face=None,
      regtime=None,
      sex=None,
      level=None,
      vipType=None,
      vipStatus=None
    ):
        self.mid = mid
        self.follower = follower
        self.uname = uname
        self.regtime = regtime
        self.sex = sex
        self.level = level
        self.vipType = vipType
        self.vipStatus = vipStatus

    def getSubmitNumber(self):
        url = "%s?mid=%s&page=1&pagesize=1" % (bilibili.submitUrl, str(self.mid))
        # print(url)
        try:
            return bilibili.getDict(bilibili.getHTMLText(url))['data']['count']
        except:
            return -1

    # 获取该up主的投稿信息
    def getSubmit(self):
        url = "%s?mid=%s&page=1&pagesize=%s" % (bilibili.submitUrl, str(self.mid),
                                                str(self.getSubmitNumber()))
        # print(url)
        submitDict = ""
        resList = []
        try:
            submitDict = bilibili.getDict(bilibili.getHTMLText(url))
            # print(submitDict)
            vlist = submitDict['data']['vlist']

            # 遍历每一个投稿
            for item in vlist:
                resList.append(
                    submit(item['typeid'], item['play'], item['title'],
                           item['created'], item['video_review'],
                           item['favorites'], item['aid'], self.mid))

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
                    submitEx(item['typeid'], item['play'], item['title'],
                             item['created'], item['video_review'],
                             item['favorites'], aid, self.mid, detail['reply'],
                             detail['coin'], detail['like'],
                             detail['his_rank']))

        except:
            return resList
        return resList


# 根据mid取得up主对象
def getUp(mid):
    url = "%s?vmid=%s" % (bilibili.upInfoUrl, str(mid))
    text = bilibili.getHTMLText(url)
    if text == "failed":
        return "failed"
    try:
        updict = bilibili.getDict(text)
        return up(updict['data']['mid'], updict['data']['follower'])
    except:
        return ""