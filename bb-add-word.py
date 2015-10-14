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
parser.add_option("--anto", type = "string", dest = "antonyme")

(options, args) = parser.parse_args()

pattern = \
u"""== {{langue|ru}} ==

=== {{S|étymologie}} ===
: %s

=== {{S|verbe|ru}} ===
'''%s''' {{pron|%s|ru}} {{%s|ru}} / [[%s|%s]] {{%s|ru|nocat=1}}
# %s
"""

class FrWikicode:
	def __init__(self, word, trad, antonyme = None):
		self.word = word
		self.trad = trad
		self.antonyme = antonyme

	def get_antonyme(self):
		s = u"==== {{S|antonymes}} ====\n"
		s += u"* [[%s]]\n\n" % self.antonyme
		return s

	def text(self):
		wikicode = u"== {{langue|%s}} ==\n\n" % self.code_lang()
		wikicode += u"=== {{S|étymologie}} ===\n"
		wikicode += u": %s\n\n" % self.etym()
		wikicode += self.core()
		if self.antonyme:
			wikicode += self.get_antonyme()
		return wikicode

class FrRuWikicode(FrWikicode):
	def code_lang(self):
		return u"ru"

class FrRuVerbWikicode(FrRuWikicode):
	def etym(self):
		prefixes = (u"пере", u"про", u"под", u"вы", u"вз", u"вс", u"по", u"до", u"об", u"в", u"у", u"с")

		for prefix in prefixes:
			if self.word.startswith(prefix):
				return u"{{cf|%s-|%s}}" % (prefix, self.word[len(prefix):])
		return u"{{ébauche-étym|ru}}"

	def core(self):
		# Get english page
		pen = EnglishNounPage.from_noun(self.word)
		key = pen.key(self.word)
		wikicode = pen.wikicode(key)

		wen = EnRuVerbWikicode(wikicode)
		accent_word = wen.accent_word()
		is_perf = wen.is_perf()
		coupled_accent = wen.coupled_accent_verb()
		coupled = wen.coupled_verb()

		# Get russian page
		wru = RussianNounPage.from_noun(self.word)
		key = wru.key(self.word)
		wikicode = wru.wikicode(key)
		
		wru = RuWikicode(wikicode)
		pron = wru.pron()

		# Generate page
		if is_perf:
			aspect = u"perf"
			coupled_aspect = u"imperf"
		else:
			aspect = u"imperf"
			coupled_aspect = u"perf"

		trad = self.trad
		trad = u"[[%s|%s]]" % (trad, trad.capitalize())

		text = u"=== {{S|verbe|%s}} ===\n" % self.code_lang()
		text += u"'''%s''' {{pron|%s|ru}} {{%s|ru}} / [[%s|%s]] {{%s|ru|nocat=1}}\n" \
					% (accent_word, pron, aspect, \
							coupled, coupled_accent, coupled_aspect)
		text += u"# %s\n\n" % trad

		return text

def build(word):
	wikicode = word.text()

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
		c = Creator(word.word, wikicode)
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

	antonyme = options.antonyme
	if antonyme:
		antonyme = antonyme.decode("utf8")

	if options.verb and options.lang == "ru":
		build(FrRuVerbWikicode(word, options.trad.decode("utf8"), antonyme))

if __name__ == "__main__":
	main()

