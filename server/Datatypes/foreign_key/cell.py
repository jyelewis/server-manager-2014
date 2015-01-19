import dataModel
import genericDatatype
import cgi
import random
import string

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if rawData else None
		
		self.retriveCode = """
			$(".error").text("")
			var rowID = $(".rowDisplay").attr("data-rowID");
		"""
		if self.column.metadata['required']:
			self.retriveCode += """
				if(rowID == ""){
					$(".error").text("This field is required");
					return;
				}
			"""
		self.retriveCode += """
			return {
				rowID: rowID
			}
		"""
		
	@property
	def viewHTML(self):
		if self.rawData and not self.column.tableDeleted:
			table = dataModel.Table(self.column.metadata['fkTable'], "DP_TableID")
			row = table.getRow(self.rawData)
			cell = row.cellByColumnID(self.column.metadata['displayColumn'])
			value = str(cell)
			return '<a href="javascript:dataplus.viewRow(\''+ str(table.name) +'\', '+ str(row.id) +');" class="fkLink">' + cgi.escape(value) + '</a>'
		else:
			return ''
	
	def __str__(self):
		if self.rawData and not self.column.tableDeleted:
			table = dataModel.Table(self.column.metadata['fkTable'], "DP_TableID")
			row = table.getRow(self.rawData)
			cell = row.cellByColumnID(self.column.metadata['displayColumn'])
			value = str(cell)
			return value
		else:
			return ''
		
	@property
	def editHTML(self):
		emptyText = '[Not set]'
		cell = emptyText
		table = None
		if self.column.metadata['fkTable'] is not None:
			table = dataModel.Table(self.column.metadata['fkTable'], "DP_TableID")
		row = None
		editKey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		
		if self.rawData:
			row = table.getRow(self.rawData)
			cell = row.cellByColumnID(self.column.metadata['displayColumn'])
		
		code = '<div class="rowDisplay" style="float:left;" data-editKey="'+ editKey +'" data-rowID="'+ (row.id if row else '') +'" data-tableName="'+(table.name if table else '')+'">'
		code += str(cell)
		code += '</div>'
		
		if table is not None:
			row = table.getRow(self.rawData)
			code += '''
				<a href="javascript:selectNewRow(\''''+ editKey +'''');" style="margin-left:15px;">Change</a>
				<a href="javascript:clearRow(\''''+ editKey +'''');" style="margin-left:5px;">Clear</a>
			'''
				
			
			code += '<div class="error"></div>'
			
			code += '''<script type="text/javascript">
					if (!selectNewRow){
						function selectNewRow(editKey){
							var tableName = $(".rowDisplay[data-editKey="+editKey+"]").attr("data-tableName");
							dataplus.chooseRow(tableName, function(rowID){
								$(".rowDisplay[data-editKey="+editKey+"]").attr("data-rowID", rowID)
								jQuery.get("'''+self.column.ajaxURL+'''", {requestType: 'rowText', rowID: rowID.toString()}, function(data){
									$(".rowDisplay[data-editKey="+editKey+"]").text(data);
								});
							});
						}
					}
					if (!clearRow){
						function clearRow(editKey){
							var obj = $(".rowDisplay[data-editKey="+editKey+"]");
							obj.attr('data-rowID', '');
							obj.text("'''+emptyText+'''")
						}
					}
				</script>
			'''
			
		return code
		
		
	def setValue(self, newValue):
		self.rawData = newValue['rowID'] if newValue else ""






