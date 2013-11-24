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
from buildbot.steps.master import MasterShellCommand
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
					masterdest=os.path.join("staging", repo),
					name = "push")

			step_deploy_in_repo = MasterShellCommand(command= ['scripts/deploy', repo],
				description = "deploy to repository",
				descriptionDone = "deployed to repository",
				name = "deploy_in_repo")

			step_cleanup = ShellCommand(
					command = ["scripts/cleanup", repo, name,
						WithProperties('%(branch)s')
						],
					workdir=base_dir,
					haltOnFailure = True,
					flunkOnFailure = True,
					description = "cleanup",
					descriptionDone = "cleaned up", name = "cleanup",
					interruptSignal="TERM")

			# add the steps to the factory
			for step in (step_srcpull, step_setup_chroots, step_build_i686, step_build_x86_64,
				step_build_source, step_push, step_deploy_in_repo, step_cleanup):
				factory.addStep(step)

			builder = BuilderConfig(
					name = entry.name,
					category = repo,
					slavenames = [ i.slavename for i in slaves ],
					properties = { "pkgname": name },
					factory = factory,
					builddir = "builders/%s" % entry.name,
					slavebuilddir = "builders/%s" % entry.name,
					)

			yield builder

	@classmethod
	def clean_chroot(cls, slaves):
		base_dir = "../../../"

		factory = BuildFactory()

		step_clean_chroot = ShellCommand(
				command = ["scripts/chroot-cleaner",
					WithProperties('%(branch)s')
					],
				workdir=base_dir,
				haltOnFailure = True,
				flunkOnFailure = True,
				description = "cleanup chroots",
				descriptionDone = "cleaned chroots", name = "cleanup chroots",
				interruptSignal="TERM")

		factory.addStep(step_clean_chroot)

		builder = BuilderConfig(
				name = "clean_chroot",
				category = "clean",
				slavenames = [ i.slavename for i in slaves ],
				properties = { "pkgname": "clean_chroot" },
				factory = factory,
				builddir = "builders/clean_chroot",
				slavebuilddir = "builders/clean_chroot",
				)

		return builder

	@classmethod
	def clean_ftp_dir(cls, slaves):
		base_dir = "../../../"

		factory = BuildFactory()

		step_clean_ftp_dir = MasterShellCommand(command= ['scripts/clean_ftp_dir'],
			description = "clean ftp dir",
			descriptionDone = "cleaned ftp dir",
			name = "clean_ftp_dir")

		factory.addStep(step_clean_ftp_dir)

		builder = BuilderConfig(
				name = "clean_ftp_dir",
				category = "clean",
				slavenames = [ i.slavename for i in slaves ],
				properties = { "pkgname": "clean_ftp_dir" },
				factory = factory,
				builddir = "builders/clean_ftp_dir",
				slavebuilddir = "builders/clean_ftp_dir",
				)

		return builder
