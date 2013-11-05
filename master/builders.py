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
# This file is cloned from https://bitbucket.org/VLCore/vlbuildbot/src/aed2d12f365e06eaa77cbc3da8a899cff1097533/master/builders.py?at=master
#

""" builders.py
Generates Builder objects for use with master.cfg based on
the text file named 'manifest'
"""
from buildbot.steps.shell import ShellCommand
from buildbot.steps.transfer import DirectoryUpload
from buildbot.process.properties import WithProperties
from buildbot.process.factory import BuildFactory
from buildbot.config import BuilderConfig
from buildbot.steps.source.git import Git
import os

import manifest

class AppBuilder(object):

	@classmethod
	def all(cls, fpath, slaves):
		"""Takes an argument (fpath) which should be the path to the manifest file"""

		base_dir = "../../../"

		for entry in manifest.Manifest.all(fpath):
			split = entry.name.split('/')
			repo = split[0]
			name = split[1]

			factory = BuildFactory()

			step_srcpull = Git(repourl="http://github.com/pacNAS/pkgbuilds.git", mode='full',
					method = 'clobber', submodules=True, branch="master",
					workdir= base_dir + "git/pkgbuilds")

			step_setup_chroots = ShellCommand(
					command = ["scripts/chroot-maker",
						WithProperties('%(branch)s')
						],
					workdir=base_dir,
					haltOnFailure = True,
					flunkOnFailure = True,
					description = "setup chroots",
					descriptionDone = "setup chroots", name = "setup chroots",
					interruptSignal="TERM")

			step_build_i686 = ShellCommand(
					command = ["scripts/build-i686", repo, name,
						WithProperties('%(branch)s')
						],
					workdir=base_dir,
					haltOnFailure = True,
					flunkOnFailure = True,
					description = "build i686",
					descriptionDone = "builded i686", name = "build_i686",
					interruptSignal="TERM")
			step_build_x86_64 = ShellCommand(
					command = ["scripts/build-x86_64", repo, name,
						WithProperties('%(branch)s')
						],
					workdir=base_dir,
					haltOnFailure = True,
					flunkOnFailure = True,
					description = "build x86_64",
					descriptionDone = "builded x86_64", name = "build_x86_64",
					interruptSignal="TERM")
			step_build_source = ShellCommand(
					command = ["scripts/build", repo, name, "i686", "--allsource",
						WithProperties('%(branch)s')
						],
					workdir=base_dir,
					haltOnFailure = True,
					flunkOnFailure = True,
					description = "build sources",
					descriptionDone = "builded sources", name = "build_sources",
					interruptSignal="TERM")

			step_push = DirectoryUpload(
					slavesrc=".",
					masterdest="staging",
					name = "push")

			step_cleanup = ShellCommand(
					command = ['rm', '*', '-rf',
						WithProperties('%(branch)s')
						],
#					workdir=base_dir,
					haltOnFailure = True,
					flunkOnFailure = True,
					description = "cleanup",
					descriptionDone = "cleaned up", name = "cleanup",
					interruptSignal="TERM")

			# add the steps to the factory
			for step in (step_srcpull, step_setup_chroots, step_build_i686, step_build_x86_64,
				step_build_source, step_push, step_cleanup):
				factory.addStep(step)

			builder = BuilderConfig(
					name = entry.name,
					category = repo,
					slavenames = [ i.slavename for i in slaves ],
					properties = { "pkgname": name },
					factory = factory,
					builddir = "builders/%s" % entry.name
					)

			yield builder
