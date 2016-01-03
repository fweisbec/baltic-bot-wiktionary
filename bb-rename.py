#!/usr/bin/python
# -*- coding: utf8 -*-

import optparse

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

parser = optparse.OptionParser()
parser.add_option("-o", "--old", type = "string", dest = "old")
parser.add_option("-n", "--new", type = "string", dest = "new")
(options, args) = parser.parse_args()

def main():
	old = options.old.decode("utf-8")
	new = options.new.decode("utf-8")
	
	if old == new:
		print "Old == new, ignored"
		return
	else:
		print "%s -> %s" % (old, new)

	rename = Renamer(old, new)
	rename.commit("Conversion de notation pour prononciation usuelle au lieu de phonologie")

if __name__ == "__main__":
	main()

