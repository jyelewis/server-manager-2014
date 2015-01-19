datatype_name = "Checkbox"

import genericDatatype
import cgi

from . import cell


class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				"defaultState": False
				,"trueText": ""
				,"falseText": ""
			}

		self.cellClass = cell.Cell
		self.retriveCode = """
			var defaultState = $(".defaultState input").prop('checked');
			return {
				 defaultState: defaultState
				,trueText: $(".trueText input").val()
				,falseText: $(".falseText input").val()
			}
		"""
		
	@property
	def editHTML(self):
		checkedCode = ' checked="checked"' if self.metadata['defaultState'] else ""
		code = """
			<tr class="defaultState">
				<td>Default state</td>
				<td>
					<input type="checkbox"{0} />
				</td>
			</tr>
			<tr class="trueText">
				<td>Checked text</td>
				<td>
					<input type="text" value="{1}" placeholder="Yes" />
				</td>
			</tr>
			<tr class="falseText">
				<td>Unchecked text</td>
				<td>
					<input type="text" value="{2}" placeholder="No" />
				</td>
			</tr>
		""".format(checkedCode, self.metadata['trueText'], self.metadata['falseText'])
		
		return code
		
		
	
	
