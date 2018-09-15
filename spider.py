import threading
from queue import Queue


class spider(threading.Thread):

  def __init__(self, fun, *tupleArg, **dictArg):
    threading.Thread.__init__(self)
    self.fun = fun
    self.tupleArg = tupleArg
    self.dictArg = dictArg


  def run(self):
    self.fun(self.tupleArg, self.dictArg)