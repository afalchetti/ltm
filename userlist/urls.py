#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2017 Angelo Falchetti
# All rights reserved

from django.conf.urls import url
from . import views

urlpatterns = [
	url("^$", views.userlist, name="userlist"),
	url("^(?P<username>[\w.@+-]+)$", views.userlist, name="userlist"),
]