import genericDatatype
import cgi
import json
import base64
from database import db

class Cell(genericDatatype.Cell):
	def __init__(self, table, column, rawData = None):
		super().__init__(table, column, rawData)
		self.rawData = rawData if (rawData) else ""
		self.newFileData = None
		self.retriveCode = """
			if (typeof readFileData[cellID] != 'undefined'){
				return JSON.stringify(readFileData[cellID]);
			} else {
				return JSON.stringify({})
			}
		"""
		
		self.initCode = """
			if (typeof readFileData == 'undefined'){
				readFileData = {};
			}
			
			$(".currentFile .remove").click(function(){
				readFileData[cellID] = {filename:false};
				$(".currentFile .file").text('[No file selected]');
			});
			
			$(".currentFile .change").click(function(){
				$(".fileSelector").slideDown(200);
			});
			
			$(".fileSelector input").change(function(e){
				if (!e.target.files.length){
					return;
				}
				var file = e.target.files[0];
				
				setTimeout(function(){
					$(".fileSelector").slideUp(200);
				}, 500);
				
				$(".currentFile .file").text("Loading file...");
				
				//read file
				var reader = new FileReader();

				reader.onload = function(e) {
					var fileData = e.target.result;
					fileData = fileData.substring(fileData.indexOf(",")+1, fileData.length);
					$(".currentFile .file").text(file.name);
					readFileData[cellID] = {
						 filename: file.name
						,data: fileData
					};
				};

				reader.readAsDataURL(file);
			});
		"""
		
		self.filename = self.rawData
		
		
	
	@property
	def viewHTML(self):
		return '<a href="'+ self.column.ajaxURL + '?fileID=' + str(self.row.id) + '" class="fkLink">' + cgi.escape(self.filename) + "</a>"
	
	
	@property
	def editHTML(self):
		filename = self.filename if self.filename else '[No file selected]'
		return """
			<div class="currentFile">
				<div class="file">{0}</div>
				<a href="javascript:;" class="remove">Remove</a>
				<a href="javascript:;" class="change" style="margin-left:15px;">Change</a>
			</div>
			<div class="fileSelector" style="display:none;">
				<input type="file" />
			</div>
		""".format(filename)
	
	@property
	def fileData(self):
		c = db.cursor()
		row = c.execute("SELECT "+self.column.dbname+"_filedata FROM "+self.table.dbname+" WHERE id = ?", (self.row.id,)).fetchone()
		return row[0]
		
	
		
	def setValue(self, newValue):
		obj = json.loads(newValue)
		if 'filename' in obj: #somehow the input has been changed
			if obj['filename'] == False: #file has been cleared
				self.rawData = ""
				self.newFileData = ""
			else:
				self.rawData = obj['filename']
				self.newFileData = base64.b64decode(obj['data'])
				
		
	def onSave(self):
		if self.newFileData is not None:
			c = db.cursor()
			c.execute("UPDATE "+self.table.dbname+" SET "+self.column.dbname+"_filedata = ? WHERE id = ?", (self.newFileData,self.row.id))
	

