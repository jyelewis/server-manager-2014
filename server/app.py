import os
import sys
sys.path.append("dataplus")
os.chdir("/scripts/server/")

import time
import re
import dataModel
import tornado.template
import subprocess
import atexit
import htpasswd
import shutil


domainRegex = "^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6}(:[0-9]{1,5})?(\/.*‌)?$"

runningProcesses = {} #keyed by website id


def pollLoop():
	while True:
		website = getRowToProcess()
		checkRunningProcesses()
		if website:
			processSite(website)
			
		time.sleep(5)
		
def processSite(website):
	print("processing site:", website.cell("Description string"))
	website.cell("Error").rawData = ""
	
	#validate fields
	domainText = website.cell("Domain").rawData
	if not re.match(domainRegex, domainText):
		website.cell("Domain").rawData = "example.com"
		website.cell("Error").rawData = "Domain '{0}' is not valid".format(domainText)
	
	if website.cell("Full build").rawData == "1":
		build(website)
		if website.cell("Enabled").rawData == "1":
			website.cell("Restart").rawData = "1"
		website.cell("Full build").rawData = "0"
		website.cell("Process changes").rawData = "1" #reque for processing
		website.save()
		return
		
	for dir in os.listdir("/Websites"):
		if str(website.id) == dir.split("_")[0]:
			if os.path.join("/Websites", dir) != str(website.cell("Physical directory")):
				os.rename(os.path.join("/Websites", dir), str(website.cell("Physical directory")))
	
	if website.cell("Enabled").rawData == "1" and str(website.id) not in runningProcesses:
		#spinup
		spinupWebsite(website)
	elif website.cell("Enabled").rawData == "0" and str(website.id) in runningProcesses:
		killProcess(website)
	
	if website.cell("Restart").rawData == "1":
		killProcess(website)
		if website.cell("Enabled").rawData == "1":
			spinupWebsite(website)
		website.cell("Restart").rawData = "0"
		
	accessUsername = str(website.cell("Access username"))
	authFilePath = str(website.cell("Physical directory")) + "/authCredentials"
	if accessUsername:
		#create httpasswd file
		authFile = htpasswd.HtpasswdFile(authFilePath, True)
		authFile.update(accessUsername, str(website.cell("Access password")))
		authFile.save()
	else:
		if os.path.exists(authFilePath):
			os.remove(authFilePath)
		
	
	rebuildNginx()
	website.save()

def getRowToProcess():
	for row in dataModel.Table("Websites").dataset.rows:
		processCell = row.cell("Process changes")
		if processCell.rawData == "1":
			processCell.rawData = "0"
			row.save()
			return row
	return None
	
def build(website):
	path = str(website.cell("Physical directory"))
	webroot = str(website.cell("Web root directory"))

	
	#create the directories
	if not os.path.exists(path):
		os.mkdir(path)
		

	if not os.path.exists(webroot):
		os.mkdir(webroot)
		
	#check if attached zip exists
	if (website.cell("Build zip").rawData != ""):
		#save new version
		archiveWebsite(website)

		#recreate directory
		shutil.rmtree(webroot)
		os.mkdir(webroot)
		
		#write the zip file into /tmp
		tmpFile = "/tmp/"+ str(website.cell("Domain")) + '.zip'
		if os.path.exists(tmpFile):
			os.remove(tmpFile)
		with open(tmpFile, 'wb') as file:
			file.write(website.cell("Build zip").fileData)
		os.system('unzip "'+tmpFile+'" -d "'+webroot+ '"')
		
		os.system('sudo chmod -R 777 "'+webroot+'"')
		os.system('sudo chown -R www-data:www-data "'+webroot+'"')
		
	print("Built website", website.cell("Domain"))
	
	
def archiveWebsite(website):
	print("Archiving website", website.cell("Domain"))
	archivesTable = dataModel.Table("Website archives")
	row = archivesTable.getRow()
	row.cell("Website").rawData = website.id
	row.cell("Archive file").rawData = website.cell("Build zip").rawData
	row.cell("Archive file").newFileData = website.cell("Build zip").fileData
	row.cell("Archive date").rawData = str(int(time.time()))
	row.save()
	
def rebuildNginx():
	websites = dataModel.Table("Websites").dataset.rows
	configFile = tornado.template.Loader(".").load("nginx.conf.template").generate(websites=websites)
	f = open('/etc/nginx/nginx.conf', 'w')
	f.write(configFile.decode('ascii'))
	f.close()
	os.system("sudo nginx -s reload")
	
def spinupWebsite(website):
	p = None
	if str(website.cell("Type")) == "Python":
		p = subprocess.Popen(['python3.4', str(website.cell("Web root directory"))+"/app.py", str(website.cell("Port number"))], cwd=str(website.cell("Web root directory")))
	elif str(website.cell("Type")) == "Node.JS":
		p = subprocess.Popen(['node', str(website.cell("Web root directory"))+"/app.js", str(website.cell("Port number"))])
	if p is not None:
		runningProcesses[str(website.id)] = p
		atexit.register(killProcess, website)

def killProcess(website):
	if str(website.id) in runningProcesses:
		runningProcesses[str(website.id)].kill()
		del runningProcesses[str(website.id)]
	
def checkRunningProcesses():
	indiciesToDelete = []
	for index in runningProcesses:
		process = runningProcesses[index]
		process.poll()
		if process.returncode != None:
			site = dataModel.Table("Websites")
			row = site.getRow(index)
			row.cell("Enabled").rawData = "0"
			row.cell("Process changes").rawData = "1"
			row.save()
			indiciesToDelete.append(index)
	for index in indiciesToDelete:
		del runningProcesses[index]

#process every site when script begins
for row in dataModel.Table("Websites").dataset.rows:
	processSite(row)
	
rebuildNginx()
pollLoop()