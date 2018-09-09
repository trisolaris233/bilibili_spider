# B站爬虫

不过是玩物罢了~ 



## 使用：

改写checkVaildUp()方法来筛选用户数据





# 接口

## up主基本信息
https://api.bilibili.com/x/relation/stat

### 参数:

* vmid: up主的id

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
* mid: up主id
* page: 页码
* pagesize: 一页的大小

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
* oid： 视频的cid， 可以从页面源码中取得

一条弹幕的标签如下：

`<d p="2.43800,4,25,16777215,1536374535,1,1a46605f,4840416031539204">2333</d>`

第一个参数是出现的时间， 以秒为单位

第二个参数是弹幕的类型， 具体经过我测试得到的类型如下

> 1: 滚动弹幕
>
> 4: 底部弹幕，字幕弹幕
>
> 5: 顶部弹幕
>
> 7: 高级弹幕

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
* aid: 视频的av号

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
* aid: 视频的av号

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








