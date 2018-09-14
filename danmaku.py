# 单条弹幕
#   sendtime: 发送时间
#   content: 内容
#   dtype: 弹幕类型
#   adi: 视频的AV号
class danmaku(object):
    def __init__(self, sendtime="", content="", dtype=0, aid=0):
        self.sendtime = sendtime
        self.content = content
        self.type = dtype
        self.aid = aid