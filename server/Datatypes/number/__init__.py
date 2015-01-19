datatype_name = "Number" 

import genericDatatype
import cgi

from .cell import Cell

class Column(genericDatatype.Column):
	def __init__(self, table, data):
		super().__init__(table, data)
		self.cellClass = Cell
		if not self.metadata or 'isRequired' not in self.metadata:
			self.metadata = {
				 "isRequired": False
				,"isDecimal": False
				,"minValue": None
				,"maxValue": None
				,"defaultValue": None
			}
			
		self.retriveCode = """
			var hasError = false;
			$('.error').text("");
			function validateInt(obj){
				var val = obj.val();
				if (val == ""){ return null; }
				var int = parseInt(val);
				if (isNaN(int)){
					obj.parent().children('.error').text("Please enter a whole number");
					obj.focus();
					hasError = true;
					return false;
				}
				return int;
			}
			
			var isRequired = $("tr.required input").prop('checked');
			var isDecimal = $("tr.isDecimal input").prop('checked');
			
			var minValue = validateInt($(".range input.min"));
			var maxValue = validateInt($(".range input.max"));
			var defaultValue = validateInt($(".defaultValue input"));
			
			if (!hasError && (minValue!=null) && (maxValue!=null)){
				if (minValue >= maxValue){
					$(".range .error").text("Min must be smaller then max")
					hasError = true;
				}
			}
			
			if (!hasError){
				return {
					 isRequired: isRequired
					,isDecimal: isDecimal
					,minValue: minValue
					,maxValue:maxValue
					,defaultValue:defaultValue
				}
			}	
		"""
		
	@property
	def editHTML(self):
		code = '''
			<tr class="required">
				<td>Required</td>
				<td>
					<input type="checkbox" {0}/>
				</td>
			</tr>
		'''.format('checked="checked" ' if self.metadata['isRequired'] else '')
		
		code += '''
			<tr class="isDecimal">
				<td>Is decimal</td>
				<td>
					<input type="checkbox" {0}/>
				</td>
			</tr>
		'''.format('checked="checked" ' if self.metadata['isDecimal'] else '')
		
		minValue = str(self.metadata['minValue']) if self.metadata['minValue'] is not None else ''
		maxValue = str(self.metadata['maxValue']) if self.metadata['maxValue'] is not None else ''
		
		code += '''
			<tr class="range">
				<td>Allowed range</td>
				<td>
					<input type="text" value="{0}" class="min" style="width:50px;" placeholder="min" />
					to
					<input type="text" value="{1}" class="max" style="width:50px;" placeholder="max" />
					<div class="error"></div>
				</td>
				<td style="font-size:11px;">
					Leave blank for no limits
				</td>
			</tr>
		'''.format(minValue, maxValue)
		
		
		code += '''
			<tr class="defaultValue">
				<td>Default value</td>
				<td>
					<input type="text" value="{0}" />
					<div class="error"></div>
				</td>
			</tr>
		'''.format(str(self.metadata['defaultValue']) if self.metadata['defaultValue'] is not None else '')
		
		return code
		








