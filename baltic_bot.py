#!/usr/bin/python
# -*- coding: utf8 -*-

import re, requests, os, sys, urllib

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

#https://fr.wiktionary.org/w/api.php?action=query&prop=revisions&rvprop=content&format=xml&titles=tronche

def add_trad_to_fr(p, en):
	info = None
	while True:
		edit = Editor(p.noun)
		try:
			edit.add_translation_de(en, info)
		except NotImplementedError:
			return
		print edit.diff()
		#print "http://de.wiktionary.org/wiki/%s" % en
		accept = raw_input("Commit change? (Y/n/i) ")
		if accept == "i":
			info = raw_input("Add info: ")
		elif not accept or accept in ("y", "Y"):
			edit.commit("Add german translation inspired by http://de.wiktionary.org/wiki/%s)" % en)
			break
		elif accept == "n":
			break
		
		#sec = re.findall("==== \{\{S\|(.+?)\}\} ====", self.wikicode(), re.M)
		"""
		pattern = "==== {{S|%s}} ===="
		l4t = ("traductions", "trad")
		for l in l4t:
			if self.wikicode().find(pattern % l):
				raise NotImplementedError
		l4 = ("variantes ortho", "var-ortho", "variantes", "transcriptions", "trans", "abréviations", "abrév", "augmentatifs", "augm", "diminutifs", "dimin", "synonymes", "quasi-synonymes", "q-syn", "antonymes", "gentilés", "gent", "composés",  "compos", "dérivés", "apparentés", "vocabulaire", "dérivés autres langues",  "drv-int", "expressions", "variantes dialectales", "dial", "hyperonymes", "hyper", "hyponymes", "hypo", "holonymes", "holo", "méronymes", "méro", "troponymes", "tropo")
		for l in l4[::-1]:
			idx = self.wikicode().find(pattern % l)
			if idx != -1:
				idx += len(pattern)
				self.wikicode()[idx:].split("\n=")
		"""

def check_unmirrored(src, dests):
	for dest in dests:
		p = FrenchNounPage.from_noun(dest)
		if not p.valid():
			return False

		if src not in p.get_german():
			print "\n\t%s -> %s" % (src.encode("utf-8"), dest.encode("utf-8"))
			#edit = raw_input("\n\t%s -> %s? (Y/n)" % (src.encode("utf-8"), dest.encode("utf-8")))
			#if not edit or edit in ("y", "Y"):
			add_trad_to_fr(p, src)
	return False

def main3():
	start = None
	if len(sys.argv) == 2:
		start = sys.argv[1]
	it = GermanNounFileIterator(start, "category")
	for i in it:
		sys.stdout.write("\r%s" %  (" " * 100))
		sys.stdout.write("\r%s" % i.noun)
		sys.stdout.flush()
		if not i.valid():
			continue
		if i.get_french():
			if check_unmirrored(i.noun, i.get_french()):
				return
	
def main2():
	start = None
	if len(sys.argv) == 2:
		start = sys.argv[1]
	it = GermanNounPageIterator(start)
	for i in it:
		sys.stdout.write("\r%s" %  (" " * 100))
		sys.stdout.write("\r%s" % i.noun)
		sys.stdout.flush()
		if i.get_french():
			if check_unmirrored(i.noun, i.get_french()):
				return

def main():
	it = GermanNounPageRawIterator(None)
	f = open("category", "w")
	for i in it:
		sys.stdout.write("\r%s" %  (" " * 100))
		sys.stdout.write("\r%s" % i)
		sys.stdout.flush()
		f.write(i.encode("utf-8"))
		f.write("\n")
		f.flush()
	f.close()

if __name__ == "__main__":
	main3()
