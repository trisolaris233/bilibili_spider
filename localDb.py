import sqlite3

class localDb:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path, timeout=5)

    def isTableExists(self, tablename):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select * from %s" % (tablename))
            result = cursor.fetchone()
            if not result:
                return False
            return True
        except:
            return False

    def execute(self, sql, paras=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, paras)
        except:
            pass
        self.conn.commit()

    def fetchall(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()