import bilibili
import bException

# 评论
#   content: 评论的内容
#   senderId: 评论者的ID
#   senderName: 评论者的用户名
#   floor: 评论者的楼层
#   sendTime: 评论时间戳
#   like: 评论点赞数
#   subReplies: 子评论数量
#   aid: 评论所在的视频av号
#   rid: 评论号
#   fid: 父评论的rid
#   upmid: 上传该视频的up主的mid
class reply(object):
    def __init__(
      self,
      content = None,
      senderId = 0,
      senderName = None,
      floor = 0,
      sendTime = 0,
      like = 0,
      subReplies = 0,
      aid = 0,
      rid = 0,
      fid = 0,
      upmid = 0
    ):
        self.content = content
        self.senderId = senderId
        self.senderName = senderName
        self.floor = floor
        self.like = like
        self.subReplies = subReplies
        self.aid = aid
        self.rid = rid
        self.fid = fid
        self.upmid = upmid


    def getSubRepliesNum(self) :
        try:
            url = "%s?pn=1&type=%d&oid=%d&sort=1&ps=1&root=%d" % (
                bilibili.subreplyUrl, 1, self.aid, self.rid)

            res = bilibili.getDict(bilibili.getHTMLText(url))
            return res['data']['page']['count']

        except bException.bError as e:
            raise e

    def getSubReplies(self, sort = 1):
        try:
            url = "%s?pn=1&type=%d&oid=%d&sort=%d&ps=%d&root=%d" % (
                      bilibili.subreplyUrl,
                      1,
                      self.aid,
                      sort,
                      self.getSubRepliesNum(),
                      self.rid
                  )
            res = bilibili.getDict(bilibili.getHTMLText(url))

            repliesList = []
            subRepliesDict = res['data']['replies']
            for r in subRepliesDict:
              nr = reply(
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
                      self.upmid
                  )
              repliesList.append(nr)

            return repliesList

        except bException.bError as e:
            raise e
