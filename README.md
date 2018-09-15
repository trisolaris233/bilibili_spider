# B站爬虫

不过是玩物罢了~ 



## 使用：

改写checkVaildUp()方法来筛选用户数据





# 接口

## up主基本信息
https://api.bilibili.com/x/relation/stat

### 参数:

| 参数名 | 类型 |   说明   |
| :----: | :--: | :------: |
|  vmid  | 整型 | up主的id |



### 返回值:

```json
{
  "code": 0,
  "message": "0",
  "ttl": 1,
  "data": {
    "mid": 唯一标识符,
    "following": 关注的人,
    "whisper": 0,
    "black": 0,
    "follower": 粉丝数
  }
}
```



---------------------------------------
 ## up主投稿的视频
https://space.bilibili.com/ajax/member/getSubmitVideos

### 参数：

|  参数名  | 类型 |    说明    |
| :------: | :--: | :--------: |
|   mid    | 整型 |   up主id   |
|   page   | 整型 |    页码    |
| pagesize | 整型 | 一页的大小 |



### 返回值:
```json
{
  "status": true,
  "data": {
    "tlist": {        // 一个字典， 表示用户投稿的稿件分布
      "1": {
        "tid": 分区id,
        "count": 稿件数量,
        "name": "分区名"
      },
    },
    "vlist": [{
      "comment": 评论数量,
      "typeid": 分区id,
      "play": 播放量,
      "pic": "封面url",
      "subtitle": "字幕？ 好像一般都为空",
      "description": "作品注释",
      "copyright": "",
      "title": "标题",
      "review": 0,
      "author": "up主的id",
      "mid": "up主的mid",
      "created": unix时间戳,
      "length": "视频长度",
      "video_review": 弹幕数量,
      "favorites": 收藏,
      "aid": av号,
      "hide_click": false
    }, 
    {
      .... 同上
    }],
    "count": 投稿数量,
    "pages": 页码
  }
}
```


不过可以随便发一个包， 然后取得返回包中的count字段， 然后重发， 可以获取所有投稿。

---

## 视频弹幕
https://api.bilibili.com/x/v1/dm/list.so

### 参数：
| 参数名 | 类型 |               说明               |
| :----: | :--: | :------------------------------: |
|  oid   | 整型 | 视频的cid， 可以从页面源码中取得 |

一条弹幕的标签如下：

`<d p="2.43800,4,25,16777215,1536374535,1,1a46605f,4840416031539204">2333</d>`

第一个参数是出现的时间， 以秒为单位

第二个参数是弹幕的类型， 具体经过我测试得到的类型如下

| 数值 |     弹幕类型      |
| :--: | :---------------: |
|  1   |     滚动弹幕      |
|  4   | 底部弹幕&字幕弹幕 |
|  5   |     顶部弹幕      |
|  7   |     高级弹幕      |



其他的参数我也看不明白， 来自https://blog.csdn.net/tanga842428/article/details/79442810

第三个参数是字号， 12非常小, 16特小, 18小, 25中, 36大, 45很大, 64特别大

第四个参数是字体的颜色以HTML颜色的十进制为准

第五个参数是Unix格式的时间戳。基准时间为 1970-1-1 08:00:00

第六个参数是弹幕池 0普通池 1字幕池 2特殊池【目前特殊池为高级弹幕专用】

第七个参数是发送者的ID，用于“屏蔽此弹幕的发送者”功能

第八个参数是弹幕在弹幕数据库中rowID 用于“历史弹幕”功能。


还有更多关于弹幕接口的细节， 比如获取历史弹幕云云， 可以参考这个帖子：

https://tieba.baidu.com/p/5798082633

---

## 视频基本参数
https://api.bilibili.com/x/web-interface/archive/stat

### 参数：
| 参数名 | 类型 |    说明    |
| :----: | :--: | :--------: |
|  aid   | 整型 | 视频的av号 |



### 返回值：

```json

{
  "code":0,
  "message":"0",
  "ttl":1,
  "data": {
    "aid":视频的av号,
    "view":视频的播放量,
    "danmaku":弹幕数量,
    "reply":评论数量,
    "favorite":收藏,
    "coin":硬币,
    "share":分享,
    "like":推荐,
    "now_rank":0,
    "his_rank":最高排名,
    "no_reprint":1,
    "copyright":1
  }
}
```



---

## 视频标签
https://api.bilibili.com/x/tag/archive/tags

这个接口返回出来很多东西不知所云， 大概也只有tag_name有点用处咯

### 参数：

| 参数名 | 类型 |    说明    |
| :----: | :--: | :--------: |
|  aid   | 整型 | 视频的av号 |

### 返回值:

```json
{
  "code": 0,
  "message": "0",
  "ttl": 1,
  "data": [{
    "tag_id": 标签的id， 暂时还不知道有什么作用,
    "tag_name": "标签名",
    "cover": "一般是一个图片路径.. 其他暂时不知道有啥用了",
    "content": "",
    "type": 3,
    "state": 0,
    "ctime": unix时间戳,
    "count": {
      "view": 0,
      "use": 0,
      "atten": 0
    },
    "is_atten": 0,
    "likes": 0,
    "hates": 0,
    "attribute": 0,
    "liked": 0,
    "hated": 0
  }, {
    ... 同上
  }]
}
```

------

## 视频评论

https://api.bilibili.com/x/v2/reply

### 参数:

| 参数名 | 类型 |                             说明                             |
| :----: | :--: | :----------------------------------------------------------: |
|   pn   | 整型 |                           评论页号                           |
|  type  | 整型 | 类型? 一般为1， 如果<1则返回“评论主题的type不合法”, 如果>1则显示”禁止评论“ |
|  oid   | 整型 |                          视频的av号                          |
|  sort  | 整型 |     如果是0则按回复热度排序， 如果不为0则按照楼层排序。      |



### 返回值：

```json
{
  "code": 0,
  "message": "0",
  "ttl": 1,
  "data": {
    "config": {
      "showadmin": 1,
      "showentry": 1
    },
    "hots": [ // 热评， 如果没有的话则是null
      0: 一个replies结构体， 
    ],
    "notice": {
      "id": 277,  // 暂时不知所云的id
      "title": "b站的推广字符串",
      "content": "b站的推广字符串",
      "link": "推广地址"
    },
    "page": {
      "acount": 评论数量,
      "count": 评论的用户数量,
      "num": 页数,
      "size": 每页的大小， 一般为20
    },
    "replies": [{   // replies结构体
      "rpid": 回复id,
      "oid": 回复的视频av号,
      "type": 回复类型? 有待推敲呢， 默认是1,
      "mid": 回复的用户名,
      "root": 0,  // 暂时没摸清楚呢..
      "parent": 0,  // 同上
      "count": 2,
      "rcount": 2,
      "floor": 楼层号,
      "state": 0,
      "fansgrade": 0,
      "attr": 0,
      "ctime": 评论时间戳,
      "rpid_str": "929647037",  // 也不知所云呢..
      "root_str": "0",
      "parent_str": "0",
      "like": 2,  // 评论点赞数
      "action": 0,
      "member": {
        "mid": "评论用户mid",
        "uname": "用户名",
        "sex": "性别 分为 男 女 保密",
        "sign": "个人说明",
        "avatar": "头像地址",
        "rank": "10000",  // 不知道作用.. 不过暂时保留吧！
        "DisplayRank": "0", // emmmm
        "level_info": {
          "current_level": 当前等级,
          "current_min": 0,
          "current_exp": 0,
          "next_exp": 0
        },
        "pendant": {  // 整个不知道做什么的了！！
          "pid": 190,
          "name": "",
          "image": "",
          "expire": 1558022400
        },
        "nameplate": {  // 这个也是!!
          "nid": 0,
          "name": "",
          "image": "",
          "image_small": "",
          "level": "",
          "condition": ""
        },
        "official_verify": {
          "type": -1,
          "desc": ""
        },
        "vip": {  // 看这个名字.. 大概是vip之类的喔(这TM不是废话吗！)
          "vipType": 2,
          "vipDueDate": 1558022400000,
          "dueRemark": "",
          "accessStatus": 0,
          "vipStatus": 1,
          "vipStatusWarn": ""
        },
        "fans_detail": null,
        "following": 0
      },
      "content": {
        "message": "回复内容",
        "plat": 楼中楼数量,
        "device": "设备字符串？ 不过我取到的时候是空字符串就是了..",
        "members": []
      },
      "replies": [
        "... 如果有楼中楼的话就从这里开始 "
      ]
    }],
    "top": 置顶评论， 一般为null吧?,
    "upper": {
      "mid": up主mid,
      "top": 置顶？ 不知道呢， 一般为null咯
    }
  }
```



------

## up主详细信息

https://space.bilibili.com/ajax/member/GetInfo

### 参数：

| 参数名 |  类型  |                             说明                             |
| :----: | :----: | :----------------------------------------------------------: |
|  csrf  | 字符串 | 验证用, 应该根据不同浏览器和不同ip地址构造的， 可能需要手动取得也说不定呢 |
|  mid   |  整型  |                           用户的id                           |

### 返回值：

```json
{
  "status": true,
  "data": {
    "mid": 用户的id,
    "name": "用户名",
    "sex": "男 女 或者保密",
    "rank": 10000,
    "face": "头像地址",
    "regtime": 注册时间戳,
    "spacesta": 0,
    "birthday": "生日",
    "sign": "个人说明",
    "level_info": {
      "current_level": 当前等级
    },
    "official_verify": {
      "type": -1,
      "desc": "",
      "suffix": ""
    },
    // Vip状态， 参考一下， 目前还没有研究
    "vip": {
      "vipType": 2,
      "vipStatus": 1
    },
    // 下面的几乎用不到， 不过也贴出来， 日后再研究
    "toutu": "一个图片地址",
    "toutuId": 一个整数,
    "theme": "default",
    "theme_preview": "",
    "coins": 0,
    "im9_sign": "363cdfe1bb013e8c507224392332d1cf",
    "fans_badge": true
  }
}
```

