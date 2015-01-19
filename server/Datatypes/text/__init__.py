datatype_name = "Text"

import genericDatatype
import cgi

from . import cell


class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		if not self.metadata:
			self.metadata = {
				 "maxSize": False
				,"defaultValue": ""
				,"required": False
				,"inputType": "Normal"
			}
		
		if 'defaultValue' not in self.metadata:
			self.metadata['defaultValue'] = ""
			
		if 'inputType' not in self.metadata:
			self.metadata['inputType'] = ""

		self.cellClass = cell.Cell
		self.retriveCode = """
			var maxSize = $(".maxSize input").val();
			var required = $(".required input").prop('checked');
			if(maxSize != ""){
				if (isNaN(maxSize)){
					$(".maxSize .error").text("Please enter a number");
					$(".maxSize input").focus();
					return
				}
				if(parseFloat(maxSize) != parseInt(maxSize)){
					$(".maxSize .error").text("Please enter a whole number");
					$(".maxSize input").focus();
					return
				}
				if (maxSize+0 <= 0){
					$(".maxSize .error").text("Please enter a number greater then 0");
					$(".maxSize input").focus();
					return
				}
			}
			return {
				 required: required
				,maxSize: maxSize == "" ? false : parseInt(maxSize)
				,defaultValue: $(".defaultValue input").val()
				,inputType: $(".inputType select").val()
			}
		"""
		
		
	@property
	def editHTML(self):
		maxSizeStr = str(self.metadata['maxSize']) if self.metadata['maxSize'] != False else ""
		defaultValue = self.metadata['defaultValue'] if self.metadata['defaultValue'] != False else ""
		checkedCode = ' checked="checked"' if self.metadata['required'] else ""
		code = """
			<tr class="required">
				<td>Required</td>
				<td>
					<input type="checkbox\"""" + checkedCode + """ />
				</td>
			</tr>
			<tr class="inputType">
				<td>Input type</td>
				<td>
					<select>"""
		
		for type in ('Normal', 'Multiline', 'Rich text'):
			code += '<option value="'+type+'"' + (' selected="selected"' if self.metadata['inputType']==type else '') +'>' + type + '</option>'
						
		code +=	"""</select>
				</td>
			</tr>
			<tr class="defaultValue">
				<td>Default value</td>
				<td>
					<input type="text" value="{0}" />
				</td>
			</tr>
			<tr class="maxSize">
				<td>Max size</td>
				<td>
					<input type="text" value="{1}" placeholder="No limit" />
					<div class="error"></div>
				</td>
			</tr>
		""".format(cgi.escape(defaultValue), cgi.escape(maxSizeStr))
		
		return code
		
		
	
	
