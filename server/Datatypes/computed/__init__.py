datatype_name = "Computed property" 

import genericDatatype
import cgi


defaultExpression = "'Not configured'"
defaultErrorValue = "N/A"

class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				 "expression": ""
				,"errorValue": ""
			}
		
		self.cellClass = Cell
		self.showsOnInsert = False
		self.retriveCode = """
			var expression = $(".expression textarea").val()
			var errorValue = $(".errorValue input").val()
			return {
				 expression:expression
				,errorValue:errorValue
			};
		"""
	
	@property
	def editHTML(self):
		html = """
			<tr class="errorValue">
				<td>Error value</td>
				<td>
					<input type="text" placeholder="{0}" value="{1}" />
				</td>
			</tr>
		""".format(defaultErrorValue, self.metadata['errorValue'])
		html += """
			<tr class="expression">
				<td>Expression</td>
				<td>
					<textarea placeholder="{0}">{1}</textarea>
				</td>
			</tr>""".format(defaultExpression, self.metadata['expression'])
		
		return html
		
		
class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if rawData else ""
		
	@property
	def viewHTML(self):
		cell = self.row.cellByColumnName
		expression = self.column.metadata['expression']
		expression = expression if expression != "" else defaultExpression
		
		errorText = self.column.metadata['errorValue']
		errorText = errorText if errorText != "" else defaultErrorValue
		try:
			return str(eval(expression))
		except:
			return errorText
		
	@property
	def editHTML(self):
		return self.viewHTML
	
	@property
	def largeViewHTML(self):
		return self.viewHTML.replace("\n", "<br />");
		
	def setValue(self, newValue):
		pass