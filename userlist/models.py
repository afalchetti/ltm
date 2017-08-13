#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2017, Angelo Falchetti. All rights reserved.

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	"""Custom user model.
	
	Currently, it does nothing differently, but it may be extended in the future."""
	pass
