import threading

class spThread(threading.Thread):
    def __init__(self, pfun, *para):
        threading.Thread.__init__(self)
        self.pfun = pfun
        self.para = para

    def run(self):
        try:
            self.pfun(self.para)
        except:
            pass