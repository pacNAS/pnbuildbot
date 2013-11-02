#!/usr/bin/env python

#    This file is part of pnbuildbot.
#
#    pnbuildbot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License v3 as published by
#    the Free Software Foundation.
#
#    pnbuildbot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    See http://www.gnu.org/licenses/ for complete licensing terms.
#
# This file is cloned from https://bitbucket.org/VLCore/vlbuildbot/src/aed2d12f365e06eaa77cbc3da8a899cff1097533/master/manifest.py?at=master
#

""" manifest.py
Python wrapper to the manifest file used with the buildbot master
"""
import os

class Manifest(object):
	def __init__(self):
		self.path = None

	@classmethod
	def all(cls, fpath):
		"""return a generator wrapper for all the items the provided manifest"""
		def is_junk(data):
			"""Detect junk in the provided data"""
			if data.startswith("#") or data.strip() == "" or " " in data:
				return True
			return False
		with open(fpath, 'r') as data:
			for line in data:
				if not is_junk(line):
					entry = cls()
					entry.name = line.strip()
					entry.manifestfile = fpath
					yield entry



