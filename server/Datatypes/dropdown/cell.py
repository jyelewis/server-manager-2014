import genericDatatype
import cgi

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if (rawData != None) else ""
		self.retriveCode = """
			return $("select").val();
		"""
		
		
	
	@property
	def viewHTML(self):
		return self.rawData
	
	
	@property
	def editHTML(self):
		code = "<select>"
		
		for option in self.column.metadata['values'].split(","):
			option = option.strip()
			if self.rawData == option:
				code += '<option value="'+option+'" selected="selected">'+option+'</option>'
			else:
				code += '<option value="'+option+'">'+option+'</option>'
		
		code += "<select>"
		return code
		
		
	def setValue(self, newValue):
		self.rawData = newValue


