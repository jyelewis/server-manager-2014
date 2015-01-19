datatype_name = "File"

import genericDatatype
import cgi
from database import db

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
				required: $(".required checkbox").prop("checked")
			}
		"""
		
	def ajaxHandler(self, webRequest):
		cell = self.table.getRow(webRequest.get_argument("fileID")).cellByColumnID(self.id)
		
		webRequest.set_header('Content-Type', 'application/octet-stream')
		webRequest.set_header('Content-Disposition', 'attachment; filename='+str(cell.rawData))
		webRequest.write(cell.fileData)
		
		
	@property
	def editHTML(self):
		checkedCode = 'checked="checked"' if self.metadata['required'] else ''
		code = """
			<tr class="required">
				<td>Required</td>
				<td>
					<input type="checkbox"{0} />
				</td>
			</tr>
		""".format(checkedCode)
		
		return code
		
	def create(self):
		super().create()
		#add filedata column
		c = db.cursor()
		c.execute("ALTER TABLE "+self.table.dbname+" ADD COLUMN "+self.dbname+"_filedata BLOB")
		db.commit()
		
		
	
	
