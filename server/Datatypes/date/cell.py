import genericDatatype
import cgi
import datetime

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if (rawData != None) else ""
		
		self.retriveCode = '$(".error").text("");'
		if self.column.metadata['required']:
			self.retriveCode += """
				if (!$(".datePicker").datepicker("getDate")){
					$(".error").text("This field is required")
					return;
				}
			"""
		self.retriveCode += """
			var value = $(".datePicker").datepicker("getDate");
			return (value)? value.getTime()/1000 : "";
		"""
		
		self.initCode = """
			$(".datePicker").datepicker({dateFormat: "dd/mm/yy"});
		"""
		if self.rawData:
			self.initCode += '$(".datePicker").datepicker("setDate",new Date('+self.rawData+'*1000));'
		
	
	@property
	def viewHTML(self):
		if self.rawData:
			return datetime.datetime.fromtimestamp(
				int(self.rawData)
			).strftime('%d/%m/%Y')
		else:
			return ''
			
	@property
	def largeViewHTML(self):
		if self.rawData:
			return datetime.datetime.fromtimestamp(
				int(self.rawData)
			).strftime('%A %d/%m/%Y')
		else:
			return ''
	
	
	@property
	def editHTML(self):
		#checkedCode = ' checked="checked"' if (self.rawData == "1") else ""
		return """
			<input type="text" class="datePicker" />
			<div class="error"></div>
		"""
		
		
	def setValue(self, newValue):
		self.rawData = newValue


