import bilibili
import submit
import bException
import logging
import requests



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
class upper(object):

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

    # 获取up主的稿件数量
    def getSubmitNumber(self):
        url = "%s?mid=%s&page=1&pagesize=1" % (bilibili.submitUrl, str(self.mid))
        # print(url)
        try:
            return bilibili.getDict(bilibili.getHTMLText(url))['data']['count']
        except bException.bError as e:
            raise e

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
                    submit.submit(item['typeid'], item['play'], item['title'],
                           item['created'], item['video_review'],
                           item['favorites'], item['aid'], self.mid))

        except bException.bError as e:
            raise e
        return resList

    # 获取该up主的投稿信息
    def getSubmitEx(self):
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
                aid = item['aid']
                submitDetailDict = {}
                detail = {}
                try:
                    # 取得每一个投稿的详细信息
                    url = "%s?aid=%s" % (bilibili.submitDetailUrl, str(aid))
                    submitDetailDict = bilibili.getDict(bilibili.getHTMLText(url))
                    detail = submitDetailDict['data']
                except:
                    return []

                resList.append(
                    submit.submitEx(item['typeid'], item['play'], item['title'],
                             item['created'], item['video_review'],
                             item['favorites'], aid, self.mid, detail['reply'],
                             detail['coin'], detail['like'],
                             detail['his_rank']))

        except:
            return resList
        return resList


# 根据mid取得up主对象
def getUpper(mid):
    url = "%s?vmid=%s" % (bilibili.upInfoUrl, str(mid))
    try:
        updict = bilibili.getDict(bilibili.getHTMLText(url))
        url = bilibili.upInfoDetailUrl

        postData = {
            'csrf': '099defc050cb8ad2827ca8493d06ab91',
            'mid': mid
        }
        # 获取用户详细信息
        r = requests.post(
            bilibili.upInfoDetailUrl,
            data=postData,
            headers=bilibili.detail_headers
        )
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            raise bException.bError(e.args)

        res = bilibili.getDict(r.text)
        return upper (
            updict['data']['mid'],
            updict['data']['follower'],
            res['data']['name'],
            res['data']['face'],
            res['data']['regtime'],
            res['data']['level_info']['current_level'],
            res['data']['vip']['vipType'],
            res['data']['vip']['vipStatus']
            )
    except bException.bError as e:
        print(e.args)
    return None