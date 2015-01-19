import genericDatatype
import cgi

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if rawData else self.column.metadata['defaultValue']
		self.retriveCode = """
			var value = $("input").val()
			$(".error").text("")
			
			
			if(isNaN(value)){
				$(".error").text("Only numbers are permitted")
				return
			}"""
		
		self.initCode  = """
			$(".arrow").click(function(){
				if (isNaN(parseInt($("input").val())+1)) return;
				var incAmount = ($(this).hasClass("right")? 1: -1);

				//clear selection
				if(document.selection && document.selection.empty) {
					document.selection.empty();
				} else if(window.getSelection) {
					var sel = window.getSelection();
					sel.removeAllRanges();
				}
		"""
		
		if self.column.metadata['isDecimal']:
			self.initCode += '$("input").val(parseFloat($("input").val())+incAmount);'
		else:
			self.initCode += '$("input").val(parseInt($("input").val())+incAmount);'
		self.initCode += '});'	
		
		if self.column.metadata['isRequired']:
			self.retriveCode += """
				if(value == ""){
					$(".error").text("This field is required");
					return
				}
			"""
			
		if not self.column.metadata['isDecimal']:
			self.retriveCode += """
				if(value != "" && parseInt(value) != parseFloat(value)){
					$(".error").text("Only whole numbers are permitted");
					return
				}
			"""
			
		if self.column.metadata['minValue'] != None:
			self.retriveCode += """
				if(parseInt(value) < """+str(self.column.metadata['minValue'])+"""){
					$(".error").text("Number must be greater then """+ str(self.column.metadata['minValue']) +"""");
					return
				}
			"""
		
		if self.column.metadata['maxValue'] != None:
			self.retriveCode += """
				if(parseInt(value) > """+str(self.column.metadata['maxValue'])+"""){
					$(".error").text("Number must be smaller then """+ str(self.column.metadata['maxValue']) +"""");
					return
				}
			"""

			
			
		self.retriveCode += """
			return value
		"""
		
	@property
	def viewHTML(self):
		return cgi.escape(str(self.rawData))
		
	@property
	def editHTML(self):
		value = cgi.escape(str(self.rawData)) if self.rawData != None else ""
		return """
			<div class="arrow left"></div>
			<input type="text" value="{0}" style="width:50px;" />
			<div class="arrow right"></div>
			<div class="error"></div>
		""".format(value)
		
	def setValue(self, newValue):
		try:
			self.rawData = int(newValue) if newValue != "" else ""
		except:
			self.rawData = float(newValue) if newValue != "" else ""