import genericDatatype
import cgi

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if (rawData != None) else "0"
		self.retriveCode = """
			return $("button").attr("data-state");
		"""

		if self.rawData == "1":
			self.displayText = self.column.metadata['pressedText'] if self.column.metadata['pressedText'] else "In progress"
		else:
			self.displayText = self.column.metadata['normalText'] if self.column.metadata['normalText'] else "Execute"
			
		executingText = self.column.metadata['pressedText'] if self.column.metadata['pressedText'] else "In progress"
		self.initCode = """
			$("button").click(function(){
				$(this).text(\""""+executingText+"""\")
				$(this).attr("disabled", "disabled");
				$(this).attr("data-state", "1");
			});
		"""
		
		
	
	@property
	def viewHTML(self):
		if self.rawData == "1":
			return self.displayText
		else:
			return ""
	
	
	@property
	def editHTML(self):
		btnState = "1" if self.rawData == "1" else "0"
		return """
			<button data-state="{0}"{1}>{2}</button>
		""".format(btnState, 'disabled="disabled"' if btnState=="1" else "", self.displayText)
		
		
	def setValue(self, newValue):
		self.rawData = "1" if newValue == "1" else "0"


