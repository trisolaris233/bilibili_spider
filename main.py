#-*- coding: utf-8 -*-

import b


if __name__ == "__main__":
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
