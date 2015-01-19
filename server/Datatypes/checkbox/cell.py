import genericDatatype
import cgi

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if (rawData != None) else self.column.metadata['defaultState']
		self.retriveCode = """
			return $("input").prop('checked');
		"""
		
		
	
	@property
	def viewHTML(self):
		if self.rawData == "1":
			return self.column.metadata['trueText'] if self.column.metadata['trueText'] else "Yes"
		else:
			return self.column.metadata['falseText'] if self.column.metadata['falseText'] else "No"
	
	
	@property
	def editHTML(self):
		checkedCode = ' checked="checked"' if (self.rawData == "1") else ""
		return """
			<input type="checkbox"{0} />
		""".format(checkedCode)
		
		
	def setValue(self, newValue):
		self.rawData = "1" if newValue else "0"


