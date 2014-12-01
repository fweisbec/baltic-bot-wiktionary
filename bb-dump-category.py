#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

def main():
	if len(sys.argv) != 2:
		# ex: ./bb-dump-category.py "Noms communs en français"
		print "usage: %s <categorie>" % sys.argv[0]
		return
	
	cat = sys.argv[1].decode("utf-8")
	it = FrenchCategoryRawIterator(cat)

	for i in it:
		sys.stdout.write(i.encode("utf8"))
		sys.stdout.write("\n")
		sys.stdout.flush()

if __name__ == "__main__":
	main()
