#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

parser = optparse.OptionParser()
parser.add_option("-l", "--lang", type = "string", dest = "lang")
parser.add_option("-c", "--categorie", type = "string", dest = "categorie")
(options, args) = parser.parse_args()

def main():	
	lang = options.lang.decode("utf-8")
	cat = options.categorie.decode("utf-8")

	if lang == "fr":
		it = FrenchCategoryRawIterator(cat)
	elif lang == "es":
		it = SpanishCategoryRawIterator(cat)
	else:
		print "???"
		return

	for i in it:
		sys.stdout.write(i.encode("utf8"))
		sys.stdout.write("\n")
		sys.stdout.flush()

if __name__ == "__main__":
	main()
