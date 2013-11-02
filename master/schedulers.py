#!/usr/bin/env python

#    This file is part of vlbuildbot.
#
#    vlbuildbot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License v3 as published by
#    the Free Software Foundation.
#
#    vlbuildbot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    See http://www.gnu.org/licenses/ for complete licensing terms.
#
# This file is cloned from https://bitbucket.org/VLCore/vlbuildbot/src/aed2d12f365e06eaa77cbc3da8a899cff1097533/master/schedulers.py?at=master
#

from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.changes import filter
import re
import os

# make a scheduler for each builder.
# This allows us to build only the changed applications rather than the entire repo.

class PNScheduler(object):

	@classmethod
	def all(cls, builders):
		def is_changed(pattern):
			def check_commit(change):
				if change.branch not in ('master',):
					return False
				for line in change.files:
					if "/%s/"%pattern in line:
						return True
				return False
			return check_commit

		for pnbuilder in builders:
			aname = pnbuilder.properties['pkgname']
			_filter = filter.ChangeFilter(
					filter_fn=is_changed(aname))
			sch = SingleBranchScheduler(
					name = pnbuilder.name,
					change_filter = _filter,
					treeStableTimer = None,
					builderNames = [ pnbuilder.name ])
			yield sch

#schedulers = [ i for i in PNScheduler.all() ]

#schedulers = []
#def is_changed(pattern):
#	def check_commit(change):
#		if change.branch != "veclinux-7.1":
#			return False
#		for line in change.files:
#			if '/%s/'%pattern in line:
#				return True
#		return False
#	return check_commit
#
#for bldr in [ i for i in builders.AppBuilder.all(os.path.join(os.getcwd(), 'manifest')) ]:
#	aname = bldr.properties['appname']
#	_filter = filter.ChangeFilter(filter_fn = is_changed(aname))
#	sch = SingleBranchScheduler(
#			name = bldr.name,
#			change_filter = _filter,
#			treeStableTimer = None,
#			builderNames = [ bldr.name ])
#	schedulers.append(sch)
#

