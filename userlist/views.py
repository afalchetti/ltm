#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import get_user_model
from django.db.models import Q

maxlistlen = 100

AuthUser = get_user_model()

def get_user_info(username):
	"""Get the interesting pieces of information of a user."""
	try:
		user = AuthUser.objects.get(username=username)
		
		return {
			"username": user.username,
			"fullname": user.get_full_name(),
			"email":    user.email,
			"phone":    user.phone,
			"address":  user.address,
			"found":    True,
		}
	
	except AuthUser.DoesNotExist:
		return {"found": False}

def get_userlist(needle):
	"""Get basic info about all the users (full name for displaying
	and username for indexing).
	
	Arguments:
		needle: string to search for in the info for each user.
	"""
	
	users = []
	
	if needle is None:
		# include one extra element (if possible) so it's easy
		# to check for "truncated lists" from the outside by just
		# comparing the array length is to the truncate length, i.e.
		# if the returned value has maxlistlen + 1 elements, the last one
		# will be removed and the list will be flagged as "truncated"
		filtered = AuthUser.objects.all()[:maxlistlen + 1]
	else:
		# this is a very simple search algorithm
		# for serious applications with longer userlists and/or more information
		# per user (e.g. a biography), some preprocessing should be done. Lucene
		# (through ElasticSearch) would be a good tool for such a job
		
		words = needle.split()
		
		filt = Q()
		
		for word in words:
			filt &= (Q(fullname__icontains=word) |
		            Q(email__icontains=word) |
		            Q(address__icontains=word) |
		            Q(phone__icontains=word))
		
		filtered = AuthUser.objects.filter(filt)[:maxlistlen + 1]
	
	for user in filtered:
		users.append({"fullname": user.get_full_name(),
		              "username": user.username})
	
	return users

def userlist(request, username=None):
	"""One page web application showing a list of users and their details."""
	
	context = {
		"landing": False,
	}
	
	if username is None:
		context["landing"] = True
	else:
		context.update(get_user_info(username))
	
	needle = request.GET.get("needle", None)
	users  = get_userlist(needle)
	
	context["truncated"] = len(users) > maxlistlen
	context["users"] = users[:maxlistlen]
	
	return render(request, "userlist/userlist.html", context)
