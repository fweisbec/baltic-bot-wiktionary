#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, requests

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

def check_decl(word):
	# en
	cases = ("nominative", "accusative", "genitive", "dative", "instrumental", "locative", "vocative")
	r = requests.get(u"http://en.wiktionary.org/wiki/%s" % word)
	en = {}
	en["nominative"] = [word]
	for case in cases:
		s = re.search("%s <small>(.+?)</tr>" % case, r.text, re.M | re.S)
		html = s.group(1)
		array = re.findall(">([^<]+?)</a></span>", html, re.M | re.S | re.U)
		if case == "nominative":
			en["nominative"].append(array[0])
		else:
			en[case] = array

	# fr
	cases = ("Nominatif", "Accusatif", u"Génitif", "Datif", "Instrumental", "Locatif", "Vocatif")
	r = requests.get(u"http://fr.wiktionary.org/wiki/%s" % word)
	fr = {}
	for case in cases:
		s = re.search("<th>%s</th>(.+?)</tr>" % case, r.text, re.M | re.S)
		html = s.group(1)
		array = re.findall(">([^<]+?)</a></td>", html, re.M | re.S | re.U)
		fr[case] = array

	#print fr
	#print en
	return fr["Nominatif"] == en["nominative"] and fr["Accusatif"] == en["accusative"] and\
		fr[u"Génitif"] == en["genitive"] and fr["Datif"] == en["dative"] and \
		fr["Instrumental"] == en["instrumental"] and fr["Locatif"] == en["locative"] and\
		fr["Vocatif"] == en["vocative"]

def add_decl(word):
	e = Editor(word)
	e.add_decl_1st()
	print e.diff()
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return
	elif not accept or accept in ("y", "Y"):
		e.commit(u"Déclinaison inspirée de http://en.wiktionary.org/wiki/%s" % word)
		print "Committed!"
	else:
		print "?"

def want_decl(word):
	en = EnglishNounPage.from_noun(word)
	
	# en word not exist
	if not en.valid():
		sys.stdout.write("- No english word")
		return False

	# tpl expected: {{lv-decl-noun|tēv|s|1st|extrawidth=-60}}
	parsed = mwparserfromhell.parse(en.wikicode())
	tplist = parsed.filter_templates(matches = u"lv-decl-noun")

	# No declension
	if not tplist:
		sys.stdout.write("- No en declension")
		return False

	# More than one declension
	if len(tplist) > 1:
		sys.stdout.write("- More than one declension")
		print tplist
		return False

	# Malformed 1st declension
	decl = tplist[0].split("|")
	if len(decl) < 4:
		sys.stdout.write("- Malformed: %s" % tplist[0])
		return False

	# Not 1st decl
	if decl[3] != "1st":
		sys.stdout.write("- Not first decl")
		return False

	# No-pl
	for d in decl:
		if d.startswith("no-pl"):
			sys.stdout.write("- No-pl")
			return False

	fr = FrenchNounPage.from_noun(word)
	parsed = mwparserfromhell.parse(fr.wikicode())
	tplist = parsed.filter_templates(matches = u"lv-décl-m-s")
	if tplist:
		sys.stdout.write("- Existing fr decl")
		return False

	sys.stdout.write("+")
	return True

def main():
	it = FrenchCategoryRawIterator(u"Noms communs en letton")
	for i in it:
		w = i.encode("utf8")
		sys.stdout.write(w + " " * (50 - len(i)))
		sys.stdout.flush()
		add = want_decl(i)
		sys.stdout.write("\n")

		if add:
			add_decl(i)
			if check_decl(i):
				print "Check OK"
			else:
				print "Check NOT OK"
				return

if __name__ == "__main__":
	main()
	#print check_decl(u"piens")
