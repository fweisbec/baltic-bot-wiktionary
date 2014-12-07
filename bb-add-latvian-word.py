#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

pattern = \
u"""== {{langue|lv}} ==
=== {{S|étymologie}} ===
: {{ébauche-étym|lv}}

=== {{S|nom|lv}} ===
'''%s''' {{pron||lv}}
# [[%s#fr|%s]]."""

# ex: cat nom_commun_fr.dump | ./bb-dump-latvian-translation.py
def main():
	lv = sys.argv[1].decode("utf-8")
	fr = sys.argv[2].decode("utf-8")
	frp = FrenchNounPage.from_noun(lv)
	if frp.valid():
		print "Page already exist"
		return

	wikicode = pattern % (lv, fr, fr.title())
	print wikicode
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return
	elif not accept or accept in ("y", "Y"):
		c = Creator(lv, wikicode)
		c.commit(u"Creation de la page du mot letton %s en miroir à la traduction de %s" % (lv, fr))
	else:
		print "?"	

if __name__ == "__main__":
	main()

