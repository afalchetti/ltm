#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2016, Angelo Falchetti. All rights reserved.

from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.utils import translation

class LocaleAdminMiddleware:
	def process_request(self, request):
		if request.path.startswith(settings.ADMIN_URL):
			request.LANG = getattr(settings, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
			translation.activate(request.LANG)
			request.LANGUAGE_CODE = request.LANG

class SSLAdminMiddleware(object):
	def process_request(self, request):
		if not request.is_secure() and request.path.startswith(settings.ADMIN_URL):
			url    = request.build_absolute_uri(request.get_full_path())
			secure = url.replace("http://", "https://")
			
			return HttpResponsePermanentRedirect(secure)
