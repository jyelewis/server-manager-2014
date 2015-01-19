import genericDatatype
import cgi
import re

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if rawData else self.column.metadata['defaultValue']
		self.retriveCode = """
				var value = $(".input").val();
				$(".error").text("");
		"""
		
		if self.column.metadata['required']:
			self.retriveCode += """
				if(!value.length > 0){
					$(".error").text("Field is required");
					$("input").focus();
					return;
				}"""
			
		if self.column.metadata["maxSize"]:
			maxSize = str(self.column.metadata["maxSize"])
			self.retriveCode += """
				if(value.length > """+ maxSize +"""){
					$(".error").text("Maximum text length is """+ maxSize +"""");
					$("input").focus();
					return;
				}"""
		self.retriveCode += """return value;"""
		
	
	
	@property
	def viewHTML(self):
		return cgi.escape(strip_tags(self.rawData))
	
	
	@property
	def largeViewHTML(self):
		inputType = self.column.metadata['inputType']
		if inputType == "Normal":
			return cgi.escape(self.rawData);
		elif inputType == "Multiline":
			return cgi.escape(self.rawData).replace("\n", "<br />");
		elif inputType == "Rich text":
			return self.rawData
	
	
	
	@property
	def editHTML(self):
		inputType = self.column.metadata['inputType']
		if inputType == "Normal":
			return """
				<input type="text" value="{0}" class="input" />
				<div class="error"></div>
			""".format(cgi.escape(str(self.rawData)))
		elif inputType == "Multiline":
			return """
				<textarea class="input">{0}</textarea>
				<div class="error"></div>
			""".format(cgi.escape(str(self.rawData)))
		elif inputType == "Rich text":
			return """
				<textarea class="input ckeditor">{0}</textarea>
				<div class="error"></div>
			""".format(cgi.escape(str(self.rawData)))
		
		
	def setValue(self, newValue):
		if self.column.metadata['required'] and not len(newValue) > 0:
			raise ValueError
			return
		if self.column.metadata['maxSize'] and len(newValue) > self.column.metadata['maxSize']:
			raise ValueError
			return
		self.rawData = newValue


#functions
def strip_tags(html):
    return re.sub('<[^<]+?>', ' ', html)




