#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r"^" + settings.ADMIN_URL[1:], admin.site.urls, name="admintop"),
    url(r"", include("userlist.urls"))
]
