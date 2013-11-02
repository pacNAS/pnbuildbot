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


from buildbot.buildslave import BuildSlave

class PNSlave(object):

	@classmethod
	def all(cls, section_items):
		"""Takes a list of options (read: configparser.items()) and splits those
			 into the corresponding slaves (each line in this section is a separate 
			 	slave)
		"""

		for name, value in section_items:
			slave = BuildSlave(name, value, max_builds=1)
			yield slave
