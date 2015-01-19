datatype_name = "Foreign key" 

import genericDatatype
import cgi
import dataModel
import json

from . import cell


class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				 "required": False
				,"fkTable": None
				,"displayColumn": None
			}
		
		if not 'required' in self.metadata:
			self.metadata['required'] = False
		
		self.cellClass = cell.Cell
		
		def ajaxHandler(webRequest):
			requestType = webRequest.get_argument("requestType", False)
			if requestType == 'rowText':
				rowID = webRequest.get_argument("rowID", False)
				if rowID:
					table = dataModel.Table(self.metadata['fkTable'], "DP_TableID")
					webRequest.write(str(table.getRow(rowID).cellByColumnID(self.metadata['displayColumn'])))
	
	
		self.ajaxHandler = ajaxHandler
		
		if not self.metadata['fkTable']:
			self.retriveCode = """
				var fkTable = $(".fkTable select").val();
				var required = $(".required input").prop('checked');
				return {
					fkTable: fkTable
					,required: required
				}
			"""
		else:
			self.retriveCode = """
				var displayColumn = $(".displayColumn select").val();
				var required = $(".required input").prop('checked');
				return {
					 displayColumn: displayColumn
					,required: required
				}
			"""
		
		try:
			self.tableDeleted = False
			if self.metadata['fkTable']:
				dataModel.Table(self.metadata['fkTable'], "DP_TableID")
		except:
			self.tableDeleted = True
		
		
		
	@property
	def editHTML(self):
		if self.tableDeleted:
			return '''
				<tr class="required">
					<td>&nbsp</td>
					<td class="error">
						ERROR: Reference table has been deleted
					</td>
				</tr>
			'''
		code = """
			<tr class="required">
				<td>Required</td>
				<td>
					<input type="checkbox" {0}/>
				</td>
			</tr>
		""".format('checked="checked" ' if self.metadata['required'] else '')
		code += """
			<tr class="fkTable">
				<td>Table</td>
				<td>
					<select{0}>""".format(' disabled="disabled"' if self.metadata['fkTable'] else '')
			
		for table in [dataModel.Table(x) for x in dataModel.allTables()]:
			if table.id == self.metadata['fkTable']:
				code += '<option value="' + str(table.id) + '" selected="selected">' + table.name + '</option>'
			else:
				code += '<option value="' + str(table.id) + '">' + table.name + '</option>'
		
		code +=		"""</select>
				</td>
			</tr>
		"""
		
		if self.metadata['fkTable']:
			code += """
				<tr class="displayColumn">
					<td>Display column</td>
					<td>
						<select>"""
					
					
			for column in dataModel.Table(self.metadata['fkTable'], "DP_TableID").columns:
				if column.id == self.metadata['displayColumn']:
					code += '<option value="' + str(column.id) + '" selected="selected">' + column.name + '</option>'
				else:
					code += '<option value="' + str(column.id) + '">' + column.name + '</option>'


			code +=		"""</select>
					</td>
				</tr>
			"""
		
		return code
	
	
	def setMetadata(self, newMetadata):
		print(newMetadata)
		print(self.metadata)
		self.metadata['required'] = newMetadata['required']
		if self.metadata['fkTable'] is None:
			self.metadata['fkTable'] = int(newMetadata['fkTable'])
			self.metadata['displayColumn'] = int(dataModel.Table(self.metadata['fkTable'], "DP_TableID").columns[0].id) #set display to first column
			return False #dont move away from the page
		else:
			self.metadata['displayColumn'] = int(newMetadata['displayColumn'])
	
