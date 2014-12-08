#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse, subprocess

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

parser = optparse.OptionParser()
parser.add_option("-l", "--latvian", type = "string", dest = "latvian")
parser.add_option("-f", "--french", type = "string", dest = "french")
(options, args) = parser.parse_args()

pattern = \
u"""== {{langue|lv}} ==
=== {{S|étymologie}} ===
: {{ébauche-étym|lv}}

=== {{S|nom|lv}} ===
'''%s''' {{pron||lv}}
# [[%s#fr|%s]]."""

def main():
	lv = options.latvian.decode("utf-8")
	fr = options.french.decode("utf-8")
	frp = FrenchNounPage.from_noun(lv)
	if frp.valid():
		print "Page already exist"
		return

	wikicode = pattern % (lv, fr, fr.title())
	# Preview wikicode
	print wikicode
	# Check word on navigator
	subprocess.call(["firefox", "-new-tab", "http://fr.wiktionary.org/wiki/%s" % fr.encode("utf-8")], shell = False)
	subprocess.call(["firefox", "-new-tab", "http://en.wiktionary.org/wiki/%s" % lv.encode("utf-8")], shell = False)
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return
	elif not accept or accept in ("y", "Y"):
		c = Creator(lv, wikicode)
		c.commit(u"Création de la page du mot letton %s en miroir à la traduction de %s" % (lv, fr))
	else:
		print "?"	

if __name__ == "__main__":
	main()

