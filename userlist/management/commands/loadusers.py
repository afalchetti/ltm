#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from ltm import settings

AuthUser = get_user_model()

import json
import sys
from uuid import uuid4

def get_free_username():
	"""Get a username that has never been used in the database."""
	
	# uuid4 generates a GUID, which with high probability (close
	# to 1.0) has never been seen before (anywhere in the world)
	return "user" + str(uuid4()).replace("-", "")

@transaction.atomic
def save_model_array(objects):
	"""Save every object in an array of Models atomically (so only one
	transaction will occur, which is much faster)."""
	for elem in objects:
		elem.save()

def format_address(line1, line2, city, state, zipcode):
	"""Transform address elements into one big address text."""
	
	streetlines = line1
	cityline   = city
	
	if len(streetlines) > 0 and len(line2) > 0:
		streetlines += "\n"
	
	if len(cityline) > 0 and len(state) > 0:
		cityline += ", "
	
	streetlines += line2
	cityline    += state
	
	return "\n".join([streetlines, cityline, zipcode])

def loadusers(userfname):
	"""Read a list of users from a JSON file and load them into the user database."""
	
	try:
		with open(userfname, "r") as userfile:
			users = json.load(userfile)
	except EnvironmentError:
		print("Failed to open the users file", file=sys.stderr)
	
	new_users = []
	
	for user in users:
		name    = user.get("name", "")
		line1   = user.get("line1", "")
		line2   = user.get("line2", "")
		city    = user.get("city", "")
		state   = user.get("state", "")
		zipcode = user.get("zip", "")
		phone   = user.get("phone", "")
		email   = user.get("email", "")
		
		username = get_free_username()
		
		# Django's idea that people have first and last names is pretty narrow;
		# although this is not optimal, it's one of the more general options and most
		# compatible. The only downside (besides clarity) is that first_name and
		# last_name have a 30 chars limit
		first_name = name
		last_name  = ""
		
		address = format_address(line1, line2, city, state, zipcode)
		
		try:
			AuthUser.objects.get(first_name=first_name, last_name=last_name,
			                     address=address, phone=phone)
			print("User {} is already in the database, skipping".format(user), file=sys.stderr)
			continue
		except:
			# everything is alright, the user wasn't found in the database, proceed to 'add' step
			pass
		
		try:
			new_user = AuthUser(username=username, first_name=first_name, last_name=last_name,
			                    address=address, phone=phone)
			new_users.append(new_user)
			
			print("Added " + name)
		except:
			print("Error trying to save new user {}".format(user), file=sys.stderr)
	
	save_model_array(new_users)

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("src", type=str);
	
	def handle(self, *args, **kwargs):
		loadusers(kwargs["src"])
