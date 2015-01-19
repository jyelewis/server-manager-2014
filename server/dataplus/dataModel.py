import string
import database
import cgi
import os
import codecs
from database import db



datatypes = {}
for file in os.listdir("Datatypes"):
	if os.path.isfile(os.path.join("Datatypes",file)):
		continue
	if not (os.path.isfile(os.path.join("Datatypes", file, "__init__.py")) or os.path.isfile(os.path.join("Datatypes", file, "__init__.pyc"))):
		continue
	temp = getattr(__import__("Datatypes."+file, globals(), locals(), [], 0), file)
	
	try:
		typeName = temp.datatype_name
	except:
		typeName = file.lower()
	datatypes[typeName] = temp
	



def ColumnFromRow(table, columnRow):
	if not columnRow[4] in datatypes:
		raise ValueError("datatype '{0}' not found".format(columnRow[4]))
	return datatypes[columnRow[4]].Column(table, columnRow)


def allTables():
	c = db.cursor()
	return [r[0] for r in c.execute("SELECT Name FROM DP_Tables").fetchall()]

def sqlite_safe_string(s, errors="strict", isLiteral = False):
	s = str(s)
	encodable = s.encode("utf-8", errors).decode("utf-8")
	nul_index = encodable.find("\x00")

	if nul_index >= 0:
		error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
								   nul_index, nul_index + 1, "NUL not allowed")
		error_handler = codecs.lookup_error(errors)
		replacement, _ = error_handler(error)
		encodable = encodable.replace("\x00", replacement)

	if isLiteral:
		return "'" + encodable.replace("'", "''") + "'"
	return "\"" + encodable.replace("\"", "\"\"") + "\""
	
def sqlite_safe_literal(s, errors="strict"):
	return sqlite_safe_string(s, errors, True)


tableEventHandlers = {}
for tableNameOrig in allTables():
	tableName = tableNameOrig.replace(' ', '_')
	if not os.path.isfile(os.path.join("tableEvents", tableName+".py")):
		continue
	tableEventHandlers[tableNameOrig] = getattr(__import__("tableEvents."+tableName, globals(), locals(), [], 0), tableName)
	

#----------------------------------------------------------------------------------------------------------------
class Table:
	def __init__(self, selector = False, selectorType = "Name"):	
		if selector:
			c = db.cursor();
			row = c.execute("SELECT * FROM DP_Tables WHERE "+sqlite_safe_string(selectorType)+" = ?", (selector,)).fetchone()
			if row == None:
				raise ValueError("Table '"+selector+"' does not exist")
			self.id = row[0]
			self.name = row[1]
			self.dbname = row[2]
		else:
			self.id = None
			self.name = ""
			self.dbname = None
		
		#getter variables
		self._columns = None
		self._dataset = None
		self._rowCount = None
	
	@property
	def columns(self):
		if not self._columns and self.id: #only fetch if value doesn't exist and does exist
			columnObjs = []
			c = db.cursor();
			columns = c.execute("SELECT * FROM DP_Columns WHERE DP_TableID = ? ORDER BY Ordering IS NULL, Ordering" , (self.id,)).fetchall()
			for column in columns:
				columnObjs.append(ColumnFromRow(self, column))
			self._columns = columnObjs
		return self._columns
		
	@property
	def dataset(self):
		if not self._dataset:
			self._dataset = self.partialDataset(None, None)
		return self._dataset
	
	@property
	def rowCount(self):
		if not self._rowCount:
			c = db.cursor()
			self._rowCount = c.execute("SELECT count(*) FROM "+sqlite_safe_string(self.dbname)+"").fetchone()[0]
		return self._rowCount
	
	def createColumn(self, columnName, datatype):
		#dis broke
		try:
			self.getColumn(columnName)
		except:
			column = datatypes[datatype].Column(self, False)
			column.name = columnName
			column.datatype = datatype
			column.visible = True
			return column
			
		raise ValueError("Column name conflict")
		
	def getColumn(self, selector, selectorType = "Name"):
		row = None
		c = db.cursor();
		row = c.execute("SELECT * FROM DP_Columns WHERE "+sqlite_safe_string(selectorType)+" = ? and DP_TableID = ?", (selector,self.id)).fetchone()
		if row == None:
			raise ValueError("Column '"+selector+"' does not exist")
			return
		return ColumnFromRow(self, row)
	
	def getRow(self, rowID = False):
		if rowID:
			c = db.cursor()
			querySQL = "SELECT "
			for column in self.columns:
				querySQL += sqlite_safe_string(column.dbname) + ", "
			querySQL = querySQL[:-2] + " " #remove trailing comma
			querySQL += "FROM " + sqlite_safe_string(self.dbname)
			querySQL += " WHERE id = " + sqlite_safe_string(rowID)
			dbrow = c.execute(querySQL).fetchone()
			if dbrow == None:
				raise ValueError("Row not found")
		
			cellObjs =  []
			for (index, data) in enumerate(dbrow):
				cellObjs.append(self.columns[index].getCell(self, data))
		else: #return a new, empty row
			cellObjs = []
			for column in self.columns:
				cellObjs.append(column.getCell(self))
				
		return Row(self, cellObjs, rowID)
	
	def partialDataset(self, startingRow, endingRow):
		if not self.columns:
			return Dataset() #return empty dataset
		c = db.cursor()
		querySQL = "SELECT id, "
		for column in self.columns:
			querySQL += sqlite_safe_string(column.dbname) + ", "
		querySQL = querySQL[:-2] + " " #remove trailing comma
		querySQL += "FROM " + sqlite_safe_string(self.dbname)
		if startingRow != None and endingRow != None:
			querySQL += " LIMIT " + sqlite_safe_string(endingRow)
			
		rows = c.execute(querySQL).fetchall()
		rowObjs = []
		for row in rows:
			cellObjs = []
			for index,data in enumerate(row):
				if index == 0:
					continue
				cellObjs.append(self.columns[index-1].getCell(self, data))
			rowObjs.append(Row(self, cellObjs, row[0]))
		
		return Dataset(self.columns, rowObjs)
		
	
	def save(self):
		c = db.cursor();
		if self.id:
			c.execute("""UPDATE DP_Tables SET
				 Name = :name
				,DBName = :dbname
				
				WHERE DP_TableID = :id
			""", {
				 "name": self.name
				,"dbname":self.dbname
				,"id": self.id
			})
		else:
			self.dbname = Table.DBName(self.name)
			c.execute("INSERT INTO DP_Tables (`Name`, `DBName`) VALUES (?, ?)", (self.name, self.dbname))
			c.execute("CREATE TABLE '"+ self.dbname +"' ('id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL);")
			self.id = c.lastrowid
		db.commit()
	
	def delete(self):
		c = db.cursor()
		c.execute("DELETE FROM DP_Columns WHERE DP_TableID = ?", (self.id,))
		c.execute("DELETE FROM DP_Tables WHERE DP_TableID = ?", (self.id,))
		c.execute("DROP TABLE " + sqlite_safe_string(self.dbname))
		db.commit()
		
	@classmethod
	def DBName(cls, name):
		retStr = database.tablePrefix
		if name[0].isdigit():
			name = "_" + name #table names cant start with a number
		for char in name:
			if char == " ":
				retStr += "_"
			elif char.isalnum() or char in "_":
				retStr += char.lower()
		c = db.cursor()
		postFix = ""
		while c.execute("SELECT * FROM DP_Tables WHERE DBName=?", (retStr+postFix,)).fetchone() != None:
			if not postFix:
				postFix = "_1"
			postFix = "_" + str(int(postFix[1])+1)
		return retStr + postFix

#----------------------------------------------------------------------------------------------------------------
class Dataset:
	def __init__(self, columns=[], rows=[]):
		self.columns = columns
		self.rows = rows
		self.canEdit = True
		
	def sort(self, sortColumnName):
		cellIndex = None
		for index, column in enumerate(self.columns):
			if column.name == sortColumnName:
				cellIndex = index
				break

		if cellIndex is not None:		
			def sortFunc(row):
				return str(row.cells[cellIndex])
			
			self.rows.sort(key=sortFunc)
#----------------------------------------------------------------------------------------------------------------		

			
#----------------------------------------------------------------------------------------------------------------
class Row:
	def __init__(self, table, cells, rowID = False):
		self.id = rowID
		self.table = table
		self.cells = cells
		for cell in self.cells: #give each cell a reference to its row
			cell.row = self
			
	def cellByColumnName(self, columnName):
		for cell in self.cells:
			if cell.column.name == columnName:
				return cell
	
	def cellByColumnID(self, columnID):
		for cell in self.cells:
			if cell.column.id == columnID:
				return cell
	
	def cell(self, columnName):
		return self.cellByColumnName(columnName)
	
	def save(self, executeHandler = True):
		c = db.cursor()
		if self.id:
			sql = "UPDATE "+ sqlite_safe_string(self.table.dbname) +" SET "
			for cell in self.cells:
				sql += sqlite_safe_string(cell.column.dbname) + " = " + sqlite_safe_literal(cell.rawData) + ", "
			sql = sql[:-2] #remove trailing comma
			sql += "WHERE id = " + sqlite_safe_literal(self.id)
			c.execute(sql)
			for cell in self.cells:
				cell.onSave() #so cells can perform actions after save (eg file saving)
			db.commit()
			if executeHandler and self.table.name in tableEventHandlers:
				tableEventHandlers[self.table.name].onUpdate(self)
				db.commit()
		else:
			sql = "INSERT INTO " + sqlite_safe_string(self.table.dbname) + " ("
			for cell in self.cells:
				sql += sqlite_safe_string(cell.column.dbname) + ", "
			if len(self.cells):
				sql = sql[:-2] #remove trailing comma
			sql += ") VALUES ("
			for cell in self.cells:
				sql += sqlite_safe_literal(cell.rawData) + ", "
			if len(self.cells):
				sql = sql[:-2]
			sql += ")"
			c.execute(sql)
			db.commit()
			self.id = c.lastrowid
			for cell in self.cells:
				cell.onSave() #so cells can perform actions after save (eg file saving)
			db.commit()
			self.id = c.lastrowid
			if executeHandler and self.table.name in tableEventHandlers:
				tableEventHandlers[self.table.name].onInsert(self)
				db.commit()
			
	def delete(self, executeHandler = True):
		if self.id:
			c = db.cursor()
			c.execute("DELETE FROM {0} WHERE id = ?".format(sqlite_safe_string(self.table.dbname)), (self.id,))
			db.commit()
			if executeHandler and self.table.name in tableEventHandlers:
				tableEventHandlers[self.table.name].onDelete(self)
				db.commit()
		

#----------------------------------------------------------------------------------------------------------------
