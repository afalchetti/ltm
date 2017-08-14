#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2017, Angelo Falchetti. All rights reserved.

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	"""Custom user model.
	
	This user model acknowledges that people live in the world and can usually
	be contacted through offline means."""
	
	# Note: both address and phone should be char fields and nullable because
	#       not everyone uses the same formats. For more details, see
	#       https://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/
	#       and similar posts
	
	# fullname is included as a cache to speed up searching
	
	fullname = models.CharField("fullname", max_length=64,  null=True, blank=True)
	address  = models.CharField("address",  max_length=256, null=True, blank=True)
	phone    = models.CharField("phone",    max_length=64,  null=True, blank=True)
	
	def save(self, *args, **kwargs):
		if len(self.first_name) == 0 and len(self.last_name) == 0:
			raise ValueError("The user must have some formal name")
		
		if len(self.first_name) > 0 and len(self.last_name) > 0:
			self.fullname = "{} {}".format(self.first_name, self.last_name)
		elif len(self.first_name) > 0:
			self.fullname = self.first_name
		else:
			self.fullname = self.last_name
		
		super().save(*args, **kwargs)