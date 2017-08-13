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
	
	address = models.CharField("address", max_length=256, null=True, blank=True)
	phone   = models.CharField("phone",   max_length=64,  null=True, blank=True)