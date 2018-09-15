#-*- coding: utf-8 -*-

import b
import time
import datetime

def test1():
    upper = b.getUpper(398510)
    b.bilibili.printObj(upper)
    print(upper.getSubmitNumber())
    sl = upper.getSubmit()
    numReplie = 0
    numEachVideo = []
    for i in sl:
        try:
            print("comments of av%d" % (i.aid))
            s = i.getReply()
            numEachVideo.append(len(s))
            for ii in s:
                # print("\t%s" % (ii.content))
                sq = ii.getSubReplies()
                numReplie = numReplie + 1 + len(sq)
        except:
            pass

    n = 1
    for i in numEachVideo:
        print("submit%d has %d replies.\n" % (n, i))
        n = n + 1

    print("\n\n the total sum of replies is %d" % (numReplie))


def test2():
    upper = b.getUpper(398510)
    submits = upper.getSubmit()
    currentDanmaku = submits[0].getDanmaku()
    d = datetime.date.fromtimestamp(submits[0].createdTime)
    d = d + datetime.timedelta(days=1)
    # print(d.timetuple())
    # print(d)

    oldDanmaku = submits[0].getHistoryDanmaku(d)
    input()

    print("today's danmaku:\n")
    for i in currentDanmaku:
        print("\t%s" % (i.content))

    print("%s's danmaku:\n" % (d.strftime("%Y-%m-%d")))
    input()
    for i in oldDanmaku:
        print("\t%s" % (i.content))



def test3():
    upper = b.getUpper(398510)
    submits = upper.getSubmit()

    for e in submits:
        e.getAllDanmakus("%d.xml" % (e.aid))


if __name__ == "__main__":
    b.bilibili.setCookies(
        "buvid3=22049C11-DB29-4150-AA63-476FAD9899B09004infoc; LIVE_BUVID=8561d4d50816d68f0a7e65b89a3cc625; rpdid=oqqwwimikkdoskomwqwiw; fts=1531761942; UM_distinctid=164a4205ff79-02838fcf15ea48-143d7240-1fa400-164a4205ff850; CNZZDATA2724999=cnzz_eid%3D277745535-1531703337-https%253A%252F%252Fwww.bilibili.com%252F%26ntime%3D1536965419; CURRENT_QUALITY=80; sid=987kdi31; stardustvideo=0; im_notify_type_152683670=0; bp_t_offset_152683670=161055067373988965; im_local_unread_152683670=0; im_seqno_152683670=2; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1532668771,1533462291; CURRENT_FNVAL=8; LIVE_BUVID__ckMd5=6640d00e0e8e8e27; DedeUserID=152683670; DedeUserID__ckMd5=6e5488f6b82b890d; SESSDATA=10c41556%2C1538060125%2C01100c0d; bili_jct=099defc050cb8ad2827ca8493d06ab91; pgv_pvi=3287150592; _dfcaptcha=8eeb36a1d97eab5dea0c091fe9caa817; finger=7b4f413b"
    )

    test3()
