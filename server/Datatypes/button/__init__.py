datatype_name = "Button"

import genericDatatype
import cgi

from . import cell


class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				"normalText": ""
				,"pressedText": ""
			}

		self.cellClass = cell.Cell
		self.retriveCode = """
			return {
				normalText: $(".normalText input").val()
				,pressedText: $(".pressedText input").val()
			}
		"""
		
	@property
	def editHTML(self):
		code = """
			<tr class="normalText">
				<td>Normal text</td>
				<td>
					<input type="text" value="{0}" placeholder="Execute" />
				</td>
			</tr>
			<tr class="pressedText">
				<td>Pressed text</td>
				<td>
					<input type="text" value="{1}" placeholder="In progress" />
				</td>
			</tr>
		""".format(self.metadata['normalText'], self.metadata['pressedText'])
		
		return code
		
		
	
	
