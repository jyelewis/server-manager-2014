datatype_name = "Drop down list"

import genericDatatype
import cgi

from . import cell


class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				"values": ""
			}

		self.cellClass = cell.Cell
		self.retriveCode = """
			return {
				values: $(".values textarea").val()
			}
		"""
		
	@property
	def editHTML(self):
		code = """
			<tr class="values">
				<td>Values (comma serperated)</td>
				<td>
					<textarea>{0}</textarea>
				</td>
			</tr>
		""".format(self.metadata['values'])
		
		return code
		
		
	
	
