import requests
import json

upInfoUrl = "https://api.bilibili.com/x/relation/stat"
submitUrl = "https://space.bilibili.com/ajax/member/getSubmitVideos"
danmakuUrl = "https://api.bilibili.com/x/v1/dm/list.so"
submitDetailUrl = "https://api.bilibili.com/x/web-interface/archive/stat"
archieveUrl = "https://www.bilibili.com/video/av"
upInfoDetailUrl = "https://space.bilibili.com/ajax/member/GetInfo"
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
    'buvid3=22049C11-DB29-4150-AA63-476FAD9899B09004infoc; LIVE_BUVID=8561d4d50816d68f0a7e65b89a3cc625; rpdid=oqqwwimikkdoskomwqwiw; fts=1531761942; UM_distinctid=164a4205ff79-02838fcf15ea48-143d7240-1fa400-164a4205ff850; CNZZDATA2724999=cnzz_eid%3D277745535-1531703337-https%253A%252F%252Fwww.bilibili.com%252F%26ntime%3D1536927598; CURRENT_QUALITY=80; sid=987kdi31; stardustvideo=0; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1532668771,1533462291; CURRENT_FNVAL=8; finger=7b4f413b; LIVE_BUVID__ckMd5=6640d00e0e8e8e27; DedeUserID__ckMd5=6e5488f6b82b890d; SESSDATA=10c41556%2C1538060125%2C01100c0d; bili_jct=099defc050cb8ad2827ca8493d06ab91; pgv_pvi=3287150592; BANGUMI_SS_24588_REC=232472; BANGUMI_SS_24625_REC=232413; _dfcaptcha=c15ba7d173b0a40f89ce5336ca8d9741',
    'Host':
    'space.bilibili.com',
    'Referer':
    'https://space.bilibili.com/2629463/',
    'UserAgent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}

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