#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse, subprocess

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *
from ru import RuWikicode
from en import EnRuVerbWikicode

parser = optparse.OptionParser()
parser.add_option("-l", "--lang", type = "string", dest = "lang")
parser.add_option("-v", "--verb", action = "store_true", dest = "verb")
parser.add_option("-w", "--word", type = "string", dest = "word")
parser.add_option("-t", "--trad", type = "string", dest = "trad")
parser.add_option("-b", "--bot", action = "store_true", dest = "bot", default = False)
(options, args) = parser.parse_args()

pattern = \
u"""== {{langue|ru}} ==

=== {{S|étymologie}} ===
: {{ébauche-étym|ru}}

=== {{S|verbe|ru}} ===
'''%s''' {{pron|%s|ru}} {{%s|ru}} / [[%s|%s]] {{%s|ru|nocat=1}}
# %s
"""

def verb(word):
	# Get english page
	pen = EnglishNounPage.from_noun(word)
	key = pen.key(word)
	wikicode = pen.wikicode(key)

	wen = EnRuVerbWikicode(wikicode)
	accent_word = wen.accent_word()
	is_perf = wen.is_perf()
	coupled_accent = wen.coupled_accent_verb()
	coupled = wen.coupled_verb()

	# Get russian page
	wru = RussianNounPage.from_noun(word)
	key = wru.key(word)
	wikicode = wru.wikicode(key)
	
	wru = RuWikicode(wikicode)
	pron = wru.pron()

	# Generate page
	if is_perf:
		aspect = "perf"
		coupled_aspect = "imperf"
	else:
		aspect = "imperf"
		coupled_aspect = "perf"

	trad = options.trad.decode("utf8")
	trad = "[[%s|%s]]" % (trad, trad.capitalize())
	wikicode = pattern % (accent_word, pron, aspect, \
						coupled, coupled_accent, coupled_aspect, trad)

	# Go to editor
	path = "/tmp/bb"
	fp = open(path, "w")
	fp.write(wikicode.encode("utf8"))
	fp.close()
	subprocess.call(["nano", path], shell = False)

	# Preview wikicode
	wikicode = open(path).read().decode("utf8")
	print wikicode
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return
	elif not accept or accept in ("y", "Y"):
		c = Creator(word, wikicode)
		c.commit(options.bot)
	else:
		print "?"

def main():
	word = options.word.decode("utf-8")
	frp = FrenchNounPage.from_noun(word)
	key = frp.key(word)
	if frp.valid(key):
		print "Page already exist"
		return

	if options.verb:
		verb(word)

if __name__ == "__main__":
	main()

