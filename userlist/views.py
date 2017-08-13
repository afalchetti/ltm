#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import get_user_model

AuthUser = get_user_model()

def get_user_info(username):
	"""Get the interesting pieces of information of a user."""
	try:
		user = AuthUser.objects.get(username=username)
		
		return {
			"fullname": user.get_full_name(),
			"email":    user.email,
			"phone":    user.phone,
			"address":  user.address,
			"found":    True,
		}
	
	except AuthUser.DoesNotExist:
		return {"found": False}

def userlist(request, username=None):
	"""One page web application showing a list of users and their details."""
	
	context = {
		"landing": False,
	}
	
	if username is None:
		context["landing"] = True
	else:
		context.update(get_user_info(username))
	
	users = []
	for user in AuthUser.objects.all():
		users.append({"fullname": user.get_full_name(), "username": user.username})
	
	context["users"] = users
	
	return render(request, "userlist/userlist.html", context)
