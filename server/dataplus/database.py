import sqlite3


rawDb = sqlite3.connect('/Websites/1_db.jyelewis.com/database.db')

tablePrefix = "tbl_"


queryCount = 1

class DBLogger():
	def __init__(self, db):
		self.db = db

	def cursor(self):
		return CursorLogger(self.db)
		
	def commit(self):
		self.db.commit()


class CursorLogger():
     def __init__(self, db):
          self.cursor = db.cursor()

     def execute(self, sql, *args, **kwargs):
     	global queryCount
     	print(str(queryCount) + ". " + sql)
     	queryCount += 1
     	return self.cursor.execute(sql, *args, **kwargs)
     	
     	
     	
db = rawDb
#db = DBLogger(rawDb)