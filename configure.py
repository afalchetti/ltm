#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved.

import os
import string
import argparse
import binascii
import json

def genfile(templatefilename, outfilename, dictionary):
	"""Generate a file from a template.
	
	Any $variable is expanded using the give dictionary
	definitions."""
	
	with open(templatefilename, "r") as templatefile:
		text = templatefile.read()
	
	replaced = string.Template(text).safe_substitute(dictionary)
	
	with open(outfilename, "w") as outfile:
		outfile.write(replaced)

def genfaketokens(tokendir):
	"""Generate placeholder tokens to let the user know their structure."""
	
	djangofilename = os.path.join(tokendir, "django.json")
	mysqlfilename  = os.path.join(tokendir, "mysql.json")
	
	os.makedirs(tokendir, exist_ok=True)
	
	if not os.path.exists(djangofilename):
		djangotoken = binascii.b2a_base64(os.urandom(32)).decode("utf8").strip("\n=")
		
		with open(djangofilename, "w") as djangofile:
			json.dump(djangotoken, djangofile, indent=2, sort_keys=True)
	
	if not os.path.exists(mysqlfilename):
		mysql_token = {"db": "ltm",
		               "host": "localhost",
		               "port": 3306,
		               "user": "db-user",
		               "password": "db-pass"}
		
		with open(mysqlfilename, "w") as mysqlfile:
			json.dump(mysql_token, mysqlfile, indent=2, sort_keys=True)

def get_allowedhosts(servername):
	"""Parse the server name list into an appropriate python list,
	including development servers."""
	
	allowed = [name for name in servername.split(" ") if name != ""]
	
	allowed.append("localhost")
	
	return allowed

def main():
	"""Main entry point."""
	
	basedir     = os.path.dirname(os.path.realpath(__file__))
	basedirname = os.path.basename(basedir)
	
	argparser = argparse.ArgumentParser()
	argparser.add_argument("--projectname", default="{}".format(basedirname), help="django project name")
	argparser.add_argument("--debug", action="store_true", help="enable debugging output in the django server")
	argparser.add_argument("--production", action="store_true", help="enable production branch")
	
	argparser.add_argument("--sslpubcert", default="/etc/ssl/certs/local.crt", help="SSL public certificate")
	argparser.add_argument("--sslprivkey", default="/etc/ssl/private/local.key", help="SSL private key")
	argparser.add_argument("--ssldhparam", default="/etc/ssl/certs/dhparam.pem", help="Diffie-Hellman parameters for increased security")
	
	argparser.add_argument("--servername", default="{}".format(basedirname), help="Server name for the Nginx configuration file")
	
	argparser.add_argument("--nginxuser", default="nginx", help="Nginx user (to limit privileges)")
	argparser.add_argument("--nginxgroup", default="www-data", help="Nginx group (to limit privileges)")
	
	argparser.add_argument("--djangopidfile", default="/tmp/{}-django.pid".format(basedirname), help="file to save Django's PID for later management")
	argparser.add_argument("--djangosocketfile", default="$HOME/tmp/{}-django.sock".format(basedirname), help="Django socket file name")
	argparser.add_argument("--djangologfile", default="$HOME/var/log/www/{}/django.log".format(basedirname), help="Django server log file")
	
	argparser.add_argument("--mocklogdir", default="$HOME/var/log/www/{}/mock".format(basedirname), help="Mock external API log directory")
	
	args = argparser.parse_args()
	
	dictionary = {
		"debug":      "True" if args.debug else "False",
		"production": "True" if args.production else "False",
		"basedir":    basedir,
		"projectname": args.projectname,
		
		"sslpubcert": os.path.expandvars(args.sslpubcert),
		"sslprivkey": os.path.expandvars(args.sslprivkey),
		"ssldhparam": os.path.expandvars(args.ssldhparam),
		
		"servername":   args.servername,
		"allowedhosts": get_allowedhosts(args.servername),
		
		"nginxuser": args.nginxuser,
		"nginxgroup": args.nginxgroup,
		
		"djangopidfile":    os.path.expandvars(args.djangopidfile),
		"djangosocketfile": os.path.expandvars(args.djangosocketfile),
		"djangologfile":    os.path.expandvars(args.djangologfile),
		
		"settingsdir": os.path.join(basedir, args.projectname),
		"mocklogdir":  os.path.expandvars(args.mocklogdir),
	}
	
	os.makedirs(os.path.dirname(os.path.realpath(dictionary["djangopidfile"])),    exist_ok=True)
	os.makedirs(os.path.dirname(os.path.realpath(dictionary["djangosocketfile"])), exist_ok=True)
	os.makedirs(os.path.dirname(os.path.realpath(dictionary["djangologfile"])),    exist_ok=True)
	
	os.makedirs(os.path.realpath(dictionary["mocklogdir"]), exist_ok=True)
	
	genfile(os.path.join(basedir, "uwsgi.ini.in"),
	        os.path.join(basedir, "uwsgi.ini"), dictionary)
	        
	genfile(os.path.join(basedir, "nginx.conf.in"),
	        os.path.join(basedir, "nginx.conf"), dictionary)
	        
	genfile(os.path.join(basedir, "start.sh.in"),
	        os.path.join(basedir, "start.sh"), dictionary)
	        
	genfile(os.path.join(basedir, "stop.sh.in"),
	        os.path.join(basedir, "stop.sh"), dictionary)
	
	genfile(os.path.join(dictionary["settingsdir"], "settings.py.in"),
	        os.path.join(dictionary["settingsdir"], "settings.py"), dictionary)
	
	genfaketokens(os.path.join(dictionary["settingsdir"], "token"))

if __name__ == "__main__":
	main()