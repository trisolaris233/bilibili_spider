import requests
import json
import bException

upInfoUrl = "https://api.bilibili.com/x/relation/stat"
submitUrl = "https://space.bilibili.com/ajax/member/getSubmitVideos"
danmakuUrl = "https://api.bilibili.com/x/v1/dm/list.so"
submitDetailUrl = "https://api.bilibili.com/x/web-interface/archive/stat"
archieveUrl = "https://www.bilibili.com/video/av"
upInfoDetailUrl = "https://space.bilibili.com/ajax/member/GetInfo"
replyUrl = "https://api.bilibili.com/x/v2/reply"
subreplyUrl = "https://api.bilibili.com/x/v2/reply/reply"
historyDanmakuUrl = "https://api.bilibili.com/x/v2/dm/history"
databaseName = ""

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

detail_headers = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection':
    'keep-alive',
    'Cookie':
    '',
    'Host':
    'space.bilibili.com',
    'Referer':
    'https://space.bilibili.com/2629463/',
    'UserAgent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}

login_headers = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection':
    'keep-alive',
    'Cookie':
    '',
    'UserAgent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}

# 获取html页面
def getHTMLText(url, header = headers, proxy = {}):
    try:
        r = requests.get(url, headers=header, proxies = proxy)
        return r.status_code, r.text
    except:
        pass
    # try:
    #     r.raise_for_status()
    #     r.encoding = r.apparent_encoding
    #     return r.text
    # except :
    #     raise bException.bError("Failed to get HTML Text with code = %d" % (r.status_code))



# 将字符串转为字典
def getDict(text):
    try:
        return json.loads(text)
    except:
        return {}

# 打印对象
def printObj(obj):
    print(obj.__dict__)


def setCookies(cookieString):
    login_headers['Cookie'] = detail_headers['Cookie'] = cookieString
