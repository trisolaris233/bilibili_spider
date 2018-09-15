import json
import bilibili

# def setDbPath(newDbPath):
#     global dbPath
#     dbPath = newDbPath


# def setdForce(newdForce):
#     global dForce
#     dForce = newdForce


# keyList = [
#     "cookies", "dbpath", "dforce", "getd", "getu", "gets", "getr", "tgetd",
#     "tgetu", "tgets", "tgetr"
# ]

# setterList = [bilibili.setCookies, setDbPath, setdForce]


# # 读取配置文件
# def readConfig():
#     config = open('config.json', encoding="UTF-8")
#     content = config.read()
#     configDict = json.loads(content)
#     keyNumber = 0

#     for eachKey in keyList:
#         if eachKey in configDict:
#             setterList[keyNumber](configDict[eachKey])
#         keyNumber = keyNumber + 1


class config:

  def __init__(self, path):
    c = open(path, encoding = "UTF-8")
    content = c.read()
    self.store = json.loads(content)
    # print(self.store)


  def book(self):
    return self.store


  def getAttr(self, attr):
    if attr in self.store:
      return self.store[attr]
    return None

  def setAttr(self, attr, val):
    self.store[attr] = val