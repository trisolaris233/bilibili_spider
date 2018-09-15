import requests
import json


def getProxyIp():
    url = "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=%s&count=20&expiryDate=0&format=1&newLine=2" % (
        "cc53c21eafd3422785868d6347d2ff55")
    resDict = json.loads(requests.get(url).text)
    return resDict['msg']

def castToStringIp(ip):
    res = ""
    if 'ip' in ip:
        res = res + ip['ip'] + ":"

    if 'port' in ip:
        res = res + ip['port']
    return res

def checkIpUseful(ip):
    try:
        requests.get("https://www.baidu.com", proxies={'http': castToStringIp(ip)})
    except:
        return False
    return True


class proxyPool:
    def __init__(self):
        self.proxyIpList = []


    def update(self):
        if not self.proxyIpList:
            res = getProxyIp()

            for i in res:
                if checkIpUseful(i):
                    self.proxyIpList.append(i)
            return 1

        else:
            for i in self.proxyIpList:
                if not checkIpUseful(i):
                    self.proxyIpList.remove(i)

            res = getProxyIp()

            for i in res:
                if checkIpUseful(i):
                    self.proxyIpList.append(i)

            return 2


    def size(self):
        return len(self.proxyIpList)

    def get(self):
        if len(self.proxyIpList) == 0:
            self.update()
            return None
        return self.proxyIpList[0]

    def remove(self, ip):
        try:
            self.proxyIpList.remove(ip)
        except:
            pass
