#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse

import WiktionaryCookie
from Wikicode import *
from Page import *
from html.fr import *
import ru

parser = optparse.OptionParser()

parser.add_option("-l", "--lang", type = "string", dest = "lang", default = "ru")
parser.add_option("-b", "--base", type = "string", dest = "base") # base to flex
parser.add_option("-f", "--flexion", type = "string", dest = "flexion") # flexion
parser.add_option("-t", "--type", type = "string", dest = "type", default = "noun") # ex: pronoun, noun, adjective
parser.add_option("-n", "--number", type = "string", dest = "number") # ex: singular, plural
parser.add_option("-c", "--case", type = "string", dest = "case") # ex: accusative féminin: af
parser.add_option("-g", "--guess", action = "store_true", dest = "guess") # fetch cases from tab on wiki page
parser.add_option("-a", "--auto", action = "store_true", dest = "auto") # add without confirm
parser.add_option("--bot", action = "store_true", dest = "bot", default = False)

(options, args) = parser.parse_args()

# Ex: ./bb-add-flexion.py -l ru -b чей -f чьё -t pronoun -c nns,ans
			

def add_flexion(base, flexion, flexion_dict):
	wikicode = "== {{langue|%s}} ==\n" % options.lang
	
	if options.type == "pronoun":
		typ = "pronom"
	elif options.type == "noun":
		typ = "nom"
	elif options.type == "adj":
		typ = "adjectif"
	else:
		print "-t ?"
		sys.exit(-1)
		
	wikicode += "=== {{S|%s|%s|flexion}} ===\n" % (typ, options.lang)

	pron = ""
	if False and options.lang == "ru":
		pron = ru.pron(flexion)
		if pron is None:
			pron = ""

	for flexion_acc in flexion_dict:
		cases = flexion_dict[flexion_acc]
		wikicode += "'''%s''' {{pron|%s|ru}}\n" % (flexion_acc, pron)

		for case in cases:
			wikicode += u"# ''"
			if case[0] == "n":
				wikicode += u"Nominatif"
			elif case[0] == "a":
				wikicode += u"Accusatif"
			elif case[0] == "d":
				wikicode += u"Datif"
			elif case[0] == "g":
				wikicode += u"Génitif"
			elif case[0] == "l":
				wikicode += u"Locatif"
			elif case[0] == "i":
				wikicode += u"Instrumental"
			elif case[0] == "v":
				wikicode += u"Vocatif"
			elif case[0] == "p":
				wikicode += u"Partitif"
			else:
				print "case??"
				return

			if len(case) > 1:
				if case[1] == "f":
					wikicode += u" féminin"
				elif case[1] == "m":
					wikicode += u" masculin"
				elif case[1] == "n":
					wikicode += u" neutre"

			if len(case) > 2:
				if case[2] == "s":
					wikicode += u" singulier"
				elif case[2] == "p":
					wikicode += u" pluriel"

			if len(case) > 3:
				if case[3] == "a":
					wikicode += u" animé"
				elif case[3] == "i":
					wikicode += u" inanimé"

			wikicode += u" de'' [[%s]].\n" % base
		wikicode += u"\n"

	print u"Page: %s" % flexion
	print wikicode

	frp = FrenchNounPage.from_noun(flexion)
	key = frp.key(flexion)
	if frp.valid(key):
		print u"Page %s already exist" % flexion
		return

	if not options.auto:
		accept = raw_input("Commit change? (Y/n) ")
		if accept == "n":
			return
		elif accept and accept not in ("y", "Y"):
			print "?"
			return

	c = Creator(flexion, wikicode)
	c.commit(options.bot)

def main():
	base = options.base.decode("utf8").replace(u'\u0301', "")
	if options.flexion:
		flexion_acc = options.flexion.decode("utf-8")
	if options.case:
		cases = options.case
	if options.guess:
		if options.flexion or options.case:
			print "-g with -f and -c ?"
			return
		if options.lang == "ru":
			html = HtmlFrRu(base)
			for (flexion, flexion_dict) in html.flexions_args():
				add_flexion(base, flexion, flexion_dict)
	else:
		cases = [c.strip() for c in cases.split(",")]
		flexion = flexion_acc.replace(u'\u0301', "")
		flexion_dict = { flexion_acc : cases }
		add_flexion(base, flexion, flexion_dict)

if __name__ == "__main__":
	main()


