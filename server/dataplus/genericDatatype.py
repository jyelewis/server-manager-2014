import cgi
import json
import urllib
from database import db


class Column:
	def __init__(self, table, data):
		self.cellClass = Cell
		
		self.showsOnInsert = True
		self.showsOnUpdate = True
		
		try:
			self.editHTML = ""
		except:
			pass
			
		try:
			self.retriveCode = "return false"
		except:
			pass
			
		if data:
			self._initWithData(data, table)
		else:
			self._initWithData((None,None,None,None,None,None,None,None), table)
		
	@classmethod
	def fromData(cls, data, table):
		obj = cls()
		obj.id = data[0]
		obj.table = table
		obj.name = data[2]
		obj.dbname = data[3]
		obj.datatype = data[4]
		obj.metadata = json.loads(data[5])
		obj.visible = bool(data[6])
		obj.ordering = data[7]
		obj.simulated = False
		return obj
		
		
	def _initWithData(self, data, table):
		self.id = data[0]
		self.table = table
		self.name = data[2]
		self.dbname = data[3]
		self.datatype = data[4]
		self.metadata = json.loads(data[5]) if data[5] else {}
		self.visible = bool(data[6])
		self.ordering = data[7]
		self.simulated = False
		
	@property
	def ajaxURL(self):
		return "/table/" + urllib.parse.quote(self.table.name) + "/column/" + urllib.parse.quote(self.name) + "/ajax"
		
	def setMetadata(self, newMetadata):
		self.metadata = newMetadata
	
	def save(self):
		if not self.simulated:
			if not self.id:
				self.create()
				return
			c = db.cursor()
			c.execute("""UPDATE DP_Columns SET
				Name = :name
				,Datatype = :datatype
				,Metadata = :metadata
				,Visible = :visible
				,Ordering = :ordering
				WHERE DP_TableID = :tableID
				AND DP_ColumnID = :id
			""", {
				 "id": self.id
				,"tableID": self.table.id
				,"name": self.name
				,"dbname": self.dbname
				,"datatype": self.datatype
				,"metadata": json.dumps(self.metadata)
				,"visible": (1 if self.visible else 0)
				,"ordering": self.ordering
			})
			db.commit()
		else:
			print("WARNING: save() called on column which does not exist in database")
			
	def create(self):
		c = db.cursor()
		self.dbname = Column.DBName(self.table, self.name)
		c.execute("""INSERT INTO DP_Columns
			(DP_TableID, Name, DBName, Datatype, Metadata, Visible, Ordering)
			VALUES
			(:tableID, :name, :dbname, :datatype, :metadata, :visible, :ordering)
		""", {
			 "tableID": self.table.id
			,"name": self.name
			,"dbname": self.dbname
			,"datatype": self.datatype
			,"metadata": json.dumps(self.metadata)
			,"visible": (1 if self.visible else 0)
			,"ordering": self.ordering
		})
		self.id = c.lastrowid
		
		c.execute("ALTER TABLE "+self.table.dbname+" ADD COLUMN "+self.dbname+" TEXT")
		
	def getCell(self, table, cellData = None):
		return self.cellClass(table, self, cellData)
			
	def delete(self):
		if not self.simulated:
			c = db.cursor()
			c.execute("DELETE FROM DP_Columns WHERE DP_ColumnID = ?", (self.id,))
			#kinda hard to drop a column, one day I should do that
			
			db.commit()
		else:
			print("WARNING: delete() called on column which does not exist in database")
			
	@classmethod
	def DBName(cls, table, name):
		retStr = ""
		if name[0].isdigit():
			name = "_" + name #column names cant start with a number
		for char in name:
			if char == " ":
				retStr += "_"
			elif char.isalnum() or char in "_":
				retStr += char.lower()
		c = db.cursor()
		postFix = ""
		columns = c.execute("pragma table_info("+ table.dbname +")").fetchall()
		while retStr + postFix in [x[1] for x in columns]:
			if not postFix:
				postFix = "_1"
			postFix = "_" + str(int(postFix[1])+1)
		return retStr + postFix
		
		
		

#------------------------------------------------------------------------------------------------------------------------------------
class Cell:
	def __init__(self, table, column, rawData = None):
		self.table = table
		self.column = column
		self.row = None
		self.rawData = rawData
		self.retriveCode = "return false"
		self.initCode = ""
		self.initialValue = rawData #used to determine if the cell has changed
	
	def setValue(self, updateObj):
		raise NotImplementedError
	
	def __str__(self):
		return self.viewHTML
		
	def hasChanged(self):
		return (self.initialValue != self.rawData)
	
	@property
	def largeViewHTML(self):
		return self.viewHTML

	def onSave(self):
		pass
