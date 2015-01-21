#!/usr/bin/python

import time
print("Preparing to configure server, press ctrl-c to cancel within 10 seconds")
print("NOTE: MySQL requires the root password to be set, this will be asked for at the begining of the setup, after that the setup can continue by itself")
time.sleep(10)

import os
from tempfile import mkstemp
from shutil import move
from os import remove, close

def replace(file_path, pattern, subst): #replace text in file
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

def install(package):
	print("installing "+package)
	os.system("apt-get -y install " + package)

#begin process
print("updating reposetories")
os.system("apt-get update && apt-get -y upgrade")

#install required packages
install("mysql-server")
install("nginx")
install("python3")
install("nodejs")
install("npm")
install("php5-fpm")
install("php5-mysql")
install("sqlite3")

print("setting up NPM")
os.system("npm config set registry http://registry.npmjs.org/")

print("installing pip and python tools")
install("python-pip")
install("python-dev")
install("libevent-dev")
install("build-essential")
install("python3-setuptools")

print("installing php add ons")
install("php5-gd")

print("easy installing pip3")
os.system("easy_install3 pip")

#setup php5-fpm to use socket
print("Configuring php5-fpm")
replace("/etc/php5/fpm/pool.d/www.conf", "listen = 127.0.0.1:9000", "listen = /var/run/php5-fpm.sock") #listen on socket
replace("/etc/php5/fpm/pool.d/www.conf", ";listen.owner", "listen.owner") #set file owner
replace("/etc/php5/fpm/pool.d/www.conf", ";listen.group", "listen.group") #set file owner
replace("/etc/php5/fpm/pool.d/www.conf", ";listen.allowed_clients", "listen.allowed_clients") #set file owner

print("setting www.conf file permissions")
os.system("chmod 644 /etc/php5/fpm/pool.d/www.conf") #reset correct permissions

print("adding mysql extention to php")
with open("/etc/php5/fpm/php.ini", "a") as phpini:
    phpini.write("extension=mysqli.so")
    
print("setting php.ini file permissions")
os.system("chmod 644 /etc/php5/fpm/php.ini") #reset correct permissions


#restart machine
print("System is going for reboot in 30 seconds.... ctrl-c to cancel")
time.sleep(30)
os.system("reboot")
