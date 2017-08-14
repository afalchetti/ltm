#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
	pass

admin.site.register(User, UserAdmin)
