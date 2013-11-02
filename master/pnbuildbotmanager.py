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
# This file is cloned from https://bitbucket.org/VLCore/vlbuildbot/src/aed2d12f365e06eaa77cbc3da8a899cff1097533/master/vlbuildbotmanager.py?at=master
#

import urllib
import time
import json
import subprocess as sp
import os
import sys

class Manifest(object):
    """ Class represents the buildbot builder manifest"""
    def __init__(self, filepath):
        self.filepath = filepath

    def _is_entry(self, line):
        """ Check if line contains a manifest entry """
        if line.startswith("#")  or line.strip() == "":
            return False
        return True

    def get_entries(self):
        """ Read the manifest file and list all the valid manifest entries """
        lst = []
        f = open(self.filepath, 'r')
        data = f.readlines()
        f.close()
        for line in data:
            if self._is_entry(line):
                lst.append(line.strip().replace("\n",""))
        return lst

    def hasBuilder(self, buildername):
        """ Test is buildername is already in the builder manifest """
        builders = self.get_entries()
        return buildername in builders

    def addBuilder(self, buildername):
        """ Add a new builder to the end of the manifest """
        # first check to make sure the builder does not exist yet
        assert self.hasBuilder(buildername) is False, "Builder already in manifest"
        builders = self.get_entries()
        builders.append(buildername)
        f = open(self.filepath, 'w')
        f.write("\n".join(builders))
        f.close()

    def removeBuilder(self, buildername):
        """ Remove a builder from the manifest """
        assert self.hasBuilder(buildername) is True, "Builder not in manifest"
        builders = self.get_entries()
        builders.remove(buildername)
        f = open(self.filepath, 'w')
        f.write("\n".join(builders))
        f.close()


class PNbuildbotMaster(object):
    """ Class representing the buildbot master for VectorLInux"""
    def __init__(self):
        self.master_root="/srv/buildbot/master/"
        self.slaveurl="http://build.pacnas.org/buildbot/json/slaves"
        self.manifest = Manifest(os.path.join(self.master_root, 'manifest'))

    def listSlaves(self):
        """ Return a list of the slaves attached to the bot master"""
        results=json.load(urllib.urlopen(self.slaveurl))
        return results.keys()

    def isBusy(self):
        """ Returns True when the bot is currently building something """
        results=json.load(urllib.urlopen(self.slaveurl))
        for i in results.keys():
            if results[i]['runningBuilds']:
                return True
        return False

    def do_reconfigure(self):
        """ run reconfigure on the bots home """
        os.chdir(self.master_root)
        proc = sp.Popen(['buildbot','restart'], stdout=sp.PIPE, stderr=sp.STDOUT)
        proc.communicate()

    def request_reconfig(self):
        """ Request a reconfigure on the next possible break """
        while self.isBusy():
            time.sleep(30) #Poll the status every 60 seconds
        return self.do_reconfigure()

    def addBuilder(self, buildername):
        """ Add a new builder to manifest """
        self.manifest.addBuilder(buildername)
        return self.request_reconfig()

    def removeBuilder(self, buildername):
        """ delete a builder from the manifest """
        self.manifest.removeBuilder(buildername)
        return self.request_reconfig()

if __name__ =='__main__':
    from optparse import OptionParser
    bot = PNbuildbotMaster()
    parser = OptionParser()
    parser.add_option("-r","--request-reconfig", dest="rrequest", default=0,
                      help="Request the bot's master configuration to be "+ \
                          "reloaded on the next break")
    parser.add_option("-a","--add-builder", dest="addbuilder", default=0,
                      help="Add builder to the bots builder manifest.  " + \
                          "The bot will be restarted at the next possible break")
    parser.add_option("-d","--delete-builder", dest="delbuilder", default=0,
                      help="Remove builder from the builder manifest.  " + \
                          "The bot will restart at the next possible break")
    (options, args) = parser.parse_args()
    print options, args
    if options.rrequest:
	bot.request_reconfig()
    elif options.addbuilder:
#        print "requested to add builder", options.addbuilder
        bot.addBuilder(options.addbuilder)
    elif options.delbuilder:
        bot.removeBuilder(options.delbuilder)


