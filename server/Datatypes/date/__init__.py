datatype_name = "Date"

import genericDatatype
import cgi

from . import cell


class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				"required": False
			}

		self.cellClass = cell.Cell
		self.retriveCode = """
			return {
				required: $(".required input").prop('checked')
			}
		"""
		
	@property
	def editHTML(self):
		checkedCode = ' checked="checked"' if self.metadata['required'] else ""
		code = """
			<tr class="required">
				<td>Required</td>
				<td>
					<input type="checkbox"{0} />
				</td>
			</tr>
		""".format(checkedCode)
		
		return code
		
		
	
	
