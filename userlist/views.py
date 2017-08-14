#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import get_user_model
from django.db.models import Q

import string

maxlistlen   = 100
maxsearchlen = 60

AuthUser = get_user_model()

def get_userinfo(username):
	"""Get the interesting pieces of information of a user."""
	try:
		user = AuthUser.objects.get(username=username)
		
		return {
			"username": user.username,
			"fullname": user.fullname,
			"email":    user.email,
			"phone":    user.phone,
			"address":  user.address,
			"found":    True,
		}
	
	except AuthUser.DoesNotExist:
		return {"found": False}

def get_userlist(needle=None):
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
		users.append({"fullname": user.fullname,
		              "username": user.username})
	
	return users

def validate(needle):
	"""Validate the user search input.
	
	Besides checking it's not too long to bog down the system,
	any utf-8 characters is valid (punctuation will be stripped),
	to consider people from different cultures."""
	
	return needle is None or len(needle) < maxsearchlen

def searchclean(needle):
	"""Remove short words (one or two chars) and punctuation to
	improve result quality and speed."""
	
	if needle is None:
		return None
	
	words = needle.split()
	nopunctuation = str.maketrans("", "", string.punctuation)
	
	return " ".join(word.translate(nopunctuation) for word in words if len(word) > 2)

def userlist(request, username=None):
	"""One page web application showing a list of users and their details."""
	
	context = {
		"landing": False,
		"valid": True,
	}
	
	if username is None:
		context["landing"] = True
	else:
		context.update(get_userinfo(username))
	
	needle = request.GET.get("needle", None)
	
	if not validate(needle):
		context["valid"] = False
		needle = None
	
	users  = get_userlist(searchclean(needle))
	
	context["truncated"] = len(users) > maxlistlen
	context["users"] = users[:maxlistlen]
	
	return render(request, "userlist/userlist.html", context)
