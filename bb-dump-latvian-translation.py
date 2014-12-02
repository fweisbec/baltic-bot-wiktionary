#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

# ex: cat nom_commun_fr.dump | ./bb-dump-latvian-translation.py
def main():
	begin = None

	if len(sys.argv) == 2:
		begin = sys.argv[1]
	
	for i in sys.stdin:
		word = i.strip()
		if begin and begin == word:
			begin = None
		if begin is not None:
			continue
		sys.stderr.write("\r%s" %  (" " * 100))
		sys.stderr.write("\r%s" % word)
		sys.stderr.flush()

		p = FrenchNounPage.from_noun(word.decode("utf-8"))
		if not p.valid():
			continue
		lv = p.get_latvian()
		for trad in lv:
			sys.stdout.write("%s %s\n" % (p.noun.encode("utf8"), trad.encode("utf8")))
			sys.stdout.flush()

if __name__ == "__main__":
	main()
