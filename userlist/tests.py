#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.test import TestCase as djTestCase
from django.test import Client
from django.urls import reverse
from ltm import settings

from unittest import TestCase
import json

from .models import User
from .views import get_userinfo, get_userlist, userlist, maxlistlen, searchclean, validate_search

def createusers():
	"""Create some fake users."""
	
	User.objects.create(username="john_doe", first_name="John", last_name="Doe",
	                    email="johndoe@gmail.com", phone="555-35465",
	                    address="Sixth street 8956\nMountain View, California\n1234567")
	
	User.objects.create(username="sussy", first_name="Sussy", last_name="",
	                    email="sussy@hotmail.com", phone="(555) 46212-456",
	                    address="Ninth street 8925\nMountain View, California\n11526378")
	
	User.objects.create(username="incognito", first_name="Incognito", last_name="",
	                    email="", phone="",
	                    address="")
	
	User.objects.create(username="martin", first_name="Martin", last_name="Colbert",
	                    email="mcolbert@late.com", phone="555-5748392",
	                    address="Broadstreet 6675\nNew York City, New York\n574839504")
	
	User.objects.create(username="frederique", first_name="Frédérique François", last_name="Rousseau-Voltaire",
	                    email="frousseau.voltaire@gmail.com", phone="(555) 19800795-875",
	                    address="La guillotine 3928\nParis, France\n576849302")
	
	User.objects.create(username="poe", first_name="Edgar Allan", last_name="Poe",
	                    email="inevitable@macabre.com", phone="555-123049807-22",
	                    address="La rue morgue 112A Of. 34\nRichmond, Virginia\n9402863")
	
	User.objects.create(username="susskind", first_name="Albert", last_name="Susskind",
	                    email="quantum@relativity.com", phone="(555) 4637584-456",
	                    address="My office\nBerkeley, California\n5768493")

class UserTestCase(djTestCase):
	"""Tests for the User model."""
	
	def setUp(self):
		"""Fill database with fake users."""
		
		createusers()
		
	def test_noname(self):
		"""Users must at least have a first name (even if it's their real first name,
		but something for identifying them formally)."""
		
		with self.assertRaises(ValueError):
			User.objects.create(username="unnamed", first_name="", last_name="",
			                    email="", phone="",
			                    address="")
		
	def test_fullname(self):
		"""Fullname should be a cache of the first and last names combined."""
		
		user = User.objects.get(username="john_doe")
		
		self.assertEqual("John Doe", user.fullname)
	
	def test_fullname_nolastname(self):
		"""Fullname should not include a trailing space if the user has no lastname."""
		
		user = User.objects.get(username="sussy")
		
		self.assertEqual("Sussy", user.fullname)

class UserlistTestCase(djTestCase):
	"""Tests for the Userlist app functions."""
	
	def setUp(self):
		"""Fill database with fake users."""
		
		createusers()
		
		self.client = Client()
	
	def test_userinfo(self):
		"""The structure of get_userinfo should contain all the basic info for known users."""
		
		poe = get_userinfo("poe")
		
		self.assertIn("username", poe)
		self.assertIn("fullname", poe)
		self.assertIn("email",    poe)
		self.assertIn("phone",    poe)
		self.assertIn("address",  poe)
		self.assertIn("found",    poe)
	
	def test_userinfo_nouser(self):
		"""If the user wasn't found, get_userinfo should emit an appropriate
		indicator but the rest of the structure is not required."""
		
		notfoundguy = get_userinfo("whoisthisguy")
		
		self.assertIn("found", notfoundguy)
	
	def test_userlist_full(self):
		"""Passing None should return the entire userlist."""
		
		userlist = get_userlist(None)
		N        = len(User.objects.all())
		
		self.assertEqual(N, len(userlist))
	
	def test_userlist_empty(self):
		"""Passing an unknown text should give an empty list."""
		
		userlist = get_userlist("nooneshouldmatchthis")
		
		self.assertEqual(0, len(userlist))
	
	def test_userlist_structure(self):
		"""The list elements should indicate both username and fullname."""
		
		userlist = get_userlist("View")
		
		self.assertEqual(2, len(userlist))
		
		self.assertIn("username", userlist[0])
		self.assertIn("fullname", userlist[0])
	
	def test_userlist_matches(self):
		"""Basic matching test where multiple users should match the search term."""
		
		userlist  = get_userlist("View")
		usernames = {user["username"] for user in userlist}
		
		self.assertEqual(2, len(userlist))
		
		self.assertIn("john_doe", usernames)
		self.assertIn("sussy", usernames)
	
	def test_userlist_match_caseinsensitive(self):
		"""Search should be case insensitive (maybe even utf8-insensitive)."""
		
		userlist  = get_userlist("albert")
		usernames = {user["username"] for user in userlist}
		
		self.assertGreaterEqual(len(userlist), 1)
		self.assertIn("susskind", usernames)
	
	def test_userlist_match_utf8(self):
		"""Search should deal with utf8 chars transparently."""
		
		userlist  = get_userlist("Frédérique")
		usernames = {user["username"] for user in userlist}
		
		self.assertGreaterEqual(len(userlist), 1)
		self.assertIn("frederique", usernames)
	
	def test_userlist_match_phone(self):
		"""Search should search in all fields, including phone."""
		
		userlist  = get_userlist("555-5748392")
		usernames = {user["username"] for user in userlist}
		
		self.assertGreaterEqual(len(userlist), 1)
		self.assertIn("martin", usernames)
	
	def test_userlist_match_address(self):
		"""Search should search in all fields, including address."""
		userlist  = get_userlist("France")
		usernames = {user["username"] for user in userlist}
		
		self.assertGreaterEqual(len(userlist), 1)
		self.assertIn("frederique", usernames)
	
	def test_userlist_match_twowords(self):
		"""Searching for two terms should look for both of them in all fields
		and then AND the results."""
		userlist  = get_userlist("street View")
		usernames = {user["username"] for user in userlist}
		
		self.assertEqual(2, len(userlist))
		self.assertIn("john_doe", usernames)
		self.assertIn("sussy", usernames)
	
	def test_userlist_match_multiple(self):
		"""This search requires searching in two fields simultaneously."""
		
		userlist  = get_userlist("street late")
		usernames = {user["username"] for user in userlist}
		
		self.assertEqual(1, len(userlist))
		self.assertIn("martin", usernames)
	
	def test_userlist_match_toomanyresults(self):
		"""If there are too many results, the search should truncate them
		to one element over the limit.
		
		The extra element is to easily determine if the list has been truncated.
		Any further processing code can actually truncate the last element and be
		certain the list is truncated (because it truncated it itself), while respecting
		the final maximum list length."""
		
		for i in range(maxlistlen + 20):
			username = "user{}".format(i)
			User.objects.create(username=username, first_name="Person", last_name=str(i),
			                    email="", phone="",
			                    address="")
		
		userlist  = get_userlist("Person")
		
		self.assertEqual(maxlistlen + 1, len(userlist))
	
	def test_userlist_match_manywords_empty(self):
		"""Passing a complex query which contains words never seen in the database should
		return an empty list (and take a reasonable amount of time)."""
		
		userlist  = get_userlist("this is a very complex query which should return nothing")
		
		self.assertEqual(0, len(userlist))
	
	def test_userlist_match_manywords(self):
		"""Passing a complex query extracted from one of the user details should return
		the given users (and take a reasonable amount of time)."""
		
		userlist  = get_userlist("macabre La rue morgue 112A Of 34 Richmond Virginia 9402863")
		usernames = {user["username"] for user in userlist}
		
		self.assertEqual(1, len(userlist))
		self.assertIn("poe", usernames)
	
	def test_userlist_offset_all(self):
		"""Check the offset works when returning the entire list."""
		
		userlist  = get_userlist(None)
		userlist2 = get_userlist(None, offset=2)
		
		# this is not really interesting to assert, but if it is
		# False, the next for would not run any iterations, so
		# the test would succeed trivially without actually testing
		# the intended behaviour
		self.assertGreaterEqual(len(userlist), 3)
		
		for i in range(2, len(userlist)):
			self.assertEqual(userlist[i], userlist2[i - 2])
	
	def test_userlist_offset_filtered(self):
		"""Check the offset works when returning a search result."""
		
		userlist  = get_userlist("street")
		userlist2 = get_userlist("street", offset=2)
		
		# this is not really interesting to assert, but if it is
		# False, the next for would not run any iterations, so
		# the test would succeed trivially without actually testing
		# the intended behaviour
		self.assertGreaterEqual(len(userlist), 3)
		
		for i in range(2, len(userlist)):
			self.assertEqual(userlist[i], userlist2[i - 2])
	
	def test_search_validation_simple(self):
		"""Test that a simple search string validates correctly."""
		
		self.assertTrue(validate_search("Albert Susskind"))
	
	def test_search_validation_accents(self):
		"""Special chars such as accents should be ok."""
		
		self.assertTrue(validate_search("Älbèrt Sûsśkïnd"))
	
	def test_search_validation_toolong(self):
		"""Long search string could bog down the system since they
		introduce arbitrarily long server execution (when creating
		the database query)."""
		
		self.assertFalse(validate_search("Albert Thomas Robert Paddington Susskind del Río from"
		                                 "Edinburgh, the royal Sir in the name of the Queen "
		                                 "and all her people"))
	
	def test_userlist_clean_none(self):
		"""None should be left alone."""
		
		self.assertEqual(None, searchclean(None))
	
	def test_userlist_clean_punctuation(self):
		"""Punctuation should be ignored."""
		
		self.assertEqual("Susskind Albert", searchclean("Susskind, Albert"))
	
	def test_userlist_clean_stopwords(self):
		"""Short words (one or two chars) should be ignored."""
		
		self.assertEqual("Susskind Albert", searchclean("Susskind q w r t e y m zz ty Albert"))

class UserlistViewTestCase(djTestCase):
	"""Tests for the Userlist app views."""
	
	def setUp(self):
		"""Fill database with fake users and create a mock client."""
		
		createusers()
		self.client = Client()
	
	def test_userlist_landing(self):
		"""The index page should show the landing message."""
		
		response = self.client.get(reverse("userlist"))
		
		self.assertEqual(200, response.status_code)
		
		self.assertIn("landing", response.context)
		self.assertIn("valid", response.context)
		self.assertEqual(True, response.context["landing"])
		self.assertEqual(True, response.context["valid"])
	
	def test_userlist_details(self):
		"""If a user has been specified the page should show their details."""
		
		response = self.client.get(reverse("userlist", args=["poe"]))
		
		self.assertEqual(200, response.status_code)
		
		self.assertIn("landing", response.context)
		self.assertIn("valid",   response.context)
		self.assertEqual(False,  response.context["landing"])
		self.assertEqual(True,   response.context["valid"])
		
		self.assertIn("fullname", response.context)
		self.assertIn("username", response.context)
		self.assertIn("email",    response.context)
		self.assertIn("phone",    response.context)
		self.assertIn("address",  response.context)
		self.assertEqual(True,    response.context["found"])
	
	def test_userlist_notfound(self):
		"""If an invalid user has been specified, show an error."""
		
		response = self.client.get(reverse("userlist", args=["thisguydoesnotexist"]))
		
		self.assertEqual(200, response.status_code)
		
		self.assertIn("landing", response.context)
		self.assertIn("valid",   response.context)
		self.assertEqual(False,  response.context["landing"])
		self.assertEqual(True,   response.context["valid"])
		
		self.assertIn("found",  response.context)
		self.assertEqual(False, response.context["found"])
	
	def test_userlist_search_none(self):
		"""If a search didn't find anything, the user list should be empty."""
		
		response = self.client.get(reverse("userlist"), {"needle": "veryhardtofindthisanywhere"})
		
		self.assertEqual(200, response.status_code)
		
		self.assertIn("valid", response.context)
		self.assertEqual(True, response.context["valid"])
		
		self.assertIn("users", response.context)
		self.assertEqual(0,    len(response.context["users"]))
	
	def test_userlist_search_success(self):
		"""If a search was successful, the user list should be populated."""
		
		response = self.client.get(reverse("userlist"), {"needle": "street"})
		
		self.assertEqual(200, response.status_code)
		
		self.assertIn("valid", response.context)
		self.assertEqual(True, response.context["valid"])
		
		self.assertIn("users", response.context)
		self.assertEqual(3,    len(response.context["users"]))

class UserlistAPITestCase(djTestCase):
	"""Tests for the Userlist JSON API."""
	
	def setUp(self):
		"""Fill database with fake users and create a mock client."""
		
		createusers()
		self.client = Client()
	
	def test_userinfo_details(self):
		"""If a user exists, the API should return their details."""
		
		response = self.client.get(reverse("api_userinfo", args=["poe"]))
		
		self.assertEqual(200, response.status_code)
		data = json.loads(response.content.decode("utf8"))
		
		self.assertIn("valid",   data)
		self.assertEqual(True,   data["valid"])
		
		self.assertIn("fullname", data)
		self.assertIn("username", data)
		self.assertIn("email",    data)
		self.assertIn("phone",    data)
		self.assertIn("address",  data)
		self.assertEqual(True,    data["found"])
	
	def test_userinfo_notfound(self):
		"""If an invalid user has been specified, return an not-found flag."""
		
		response = self.client.get(reverse("api_userinfo", args=["thisguydoesnotexist"]))
		
		self.assertEqual(200, response.status_code)
		data = json.loads(response.content.decode("utf8"))
		
		self.assertIn("valid",   data)
		self.assertEqual(True,   data["valid"])
		
		self.assertIn("found",  data)
		self.assertEqual(False, data["found"])
	
	def test_userlist_search_none(self):
		"""If a search didn't find anything, the user list should be empty."""
		
		response = self.client.get(reverse("api_userlist"), {"needle": "veryhardtofindthisanywhere"})
		
		self.assertEqual(200, response.status_code)
		data = json.loads(response.content.decode("utf8"))
		
		self.assertIn("valid", data)
		self.assertEqual(True, data["valid"])
		
		self.assertIn("users", data)
		self.assertEqual(0,    len(data["users"]))
	
	def test_userlist_search_success(self):
		"""If a search was successful, the user list should be populated."""
		
		response = self.client.get(reverse("api_userlist"), {"needle": "street"})
		
		self.assertEqual(200, response.status_code)
		data = json.loads(response.content.decode("utf8"))
		
		self.assertIn("valid", data)
		self.assertEqual(True, data["valid"])
		
		self.assertIn("users", data)
		self.assertEqual(3,    len(data["users"]))

class TokenTestCase(TestCase):
	"""Tests for the credentials system."""
	
	def setUp(self):
		pass
	
	def test_database_token(self):
		"""If using MySQL, the credentials should
		contain all the required information."""
		
		if settings.PRODUCTION:
			self.assertIn("db",       MYSQL_TOKEN)
			self.assertIn("host",     MYSQL_TOKEN)
			self.assertIn("port",     MYSQL_TOKEN)
			self.assertIn("user",     MYSQL_TOKEN)
			self.assertIn("password", MYSQL_TOKEN)
