#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

SEARCH = u"""Le Blanc à lunettes"""
OLD = u"""\{\{source\|\{\{w\|Georges Simenon\}\}, ''\{\{w\|Le Blanc à lunettes\}\}'', \{\{w\|Gallimard\}\}, 1937. Ch. ([IVXLC]+)\}\}"""
NEW = u"""{{source|{{Citation/Georges Simenon/Le Blanc à lunettes/1937|\\1}}}}"""
EX_OLD = u"""{{source|{{w|Georges Simenon}}, ''{{w|Le Blanc à lunettes}}'', {{w|Gallimard}}, 1937. Ch. VII}}"""
REGEX = True

parser = optparse.OptionParser()
parser.add_option("-a", "--auto", action = "store_true", dest = "auto", default = False)
parser.add_option("-s", "--start", type = "string", dest = "start", default = None)
(options, args) = parser.parse_args()

nr_commits = 0

def commit(e):
	global nr_commits
	e.commit("Remplace %s par %s" % (OLD, NEW))
	print colored("Committed (%d)" % nr_commits, "green")
	nr_commits += 1

def process_one(p, title):
	sys.stdout.write(title.encode("utf8") + " " * (50 - len(title)))
	key = p.key(title)
	wikicode = p.wikicode(key)
	basetimestamp = p.revision_time(key)
	e = Editor(title, wikicode, basetimestamp)
	if REGEX:
		e.reg_replace(OLD, NEW)
	else:
		e.replace(OLD, NEW)
	diff = e.diff()
	if not diff:
		print "No change"
		return
	if options.auto:
		commit(e)
		return
	print
	print diff
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return
	elif not accept or accept in ("y", "Y"):
		commit(e)
	else:
		print "?"

def process_titles(titles):
	sys.stdout.write(colored("Loading 50 words from search\n", "yellow"))
	p = NounPage.from_nouns_dom(titles, "fr")
	for t in titles:
		process_one(p, t)
	

def main():
	it = SearchIterator(SEARCH)
	#print SearchPage(SEARCH).json

	titles = []
	for i in it:
		if options.start is not None:
			if i != options.start:
				continue
			else:
				options.start = None
		titles.append(i)
		if len(titles) == 50:
			process_titles(titles)
			titles = []
	if titles:
		process_titles(titles)

	print "Commits: %d" % nr_commits

if __name__ == "__main__":
	main()

