#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

# {{Requête fait}}
# {{Bot fait|Baltic Bot|Shalott}} ~~~~~

#OLD = [u"""(\{\s*\{ru-déclf\s*\|.*?)(\|\w+-=[^|}]*)([^}]*)"""]
OLD = [u"""(\{\s*\{ru-décln\s*\|.*?)(\|\w+-=[^|}]*)(.*?\}\})"""]
NEW = r"""\1\3"""
REGEX = True

parser = optparse.OptionParser()
parser.add_option("-a", "--auto", action = "store_true", dest = "auto", default = False)
parser.add_option("-1", "--manual1", action = "store_true", dest = "manual1", default = False)
parser.add_option("-s", "--start", type = "string", dest = "start", default = None)
parser.add_option("-e", "--search", type = "string", dest = "search", default = None)
parser.add_option("-c", "--category", type = "string", dest = "category", default = None)
parser.add_option("-g", "--ignore-case", action = "store_true", dest = "ignore_case", default = False)
parser.add_option("-i", "--input", type = "string", dest = "input", default = None)
parser.add_option("-u", "--summary", type = "string", dest = "summary", default = None)
(options, args) = parser.parse_args()

nr_commits = 0

def commit(e, old, new, diff):
	if options.summary:
		summary = options.summary
	else:
		summary = "Remplace %s par %s" % (old, new)
	e.commit(summary)
	fp = open("commits.log", "a")
	fp.write("---------\n")
	fp.write(diff.encode("utf-8"))
	fp.close()
	global nr_commits
	nr_commits += 1

nr = 0
def process_one(p, title, old, new):
	global nr, nr_commits
	nr+=1
	key = p.key(title)
	wikicode = p.wikicode(key)
	basetimestamp = p.revision_time(key)
	e = Editor(title, wikicode, basetimestamp)
	if REGEX:
		while e.reg_replace(old, new, options.ignore_case):
			continue
	else:
		e.replace(old, new)
	diff = e.diff()
	if not diff:
		return False
	if options.auto or (options.manual1 and nr_commits > 0):
		commit(e, old, new, diff)
		return True
	print
	print diff
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return False
	elif not accept or accept in ("y", "Y"):
		commit(e, old, new, diff)
		return True
	else:
		print "?"
	return False

def process_titles(titles):
	sys.stdout.write(colored("Loading 50 words from search\n", "yellow"))
	p = NounPage.from_nouns_dom(titles, "fr")
	for title in titles:
		sys.stdout.write(title.encode("utf8") + " " * (50 - len(title)))
		committed = False
		for old in OLD:
			res = process_one(p, title, old, NEW)
			if res:
				committed = True
		if not committed:
			print colored("No change", "blue")
		else:
			global nr_commits
			print colored("Committed (%d)" % nr_commits, "green")

def main():
	if options.search:
		it = SearchIterator(options.search.decode("utf8"))
	elif options.category:
		it = FrenchCategoryRawIterator(options.category.decode("utf8"))
	elif options.input:
		it = NounFileNameIterator(options.input)

	titles = []
	for i in it:
		if options.start is not None:
			if i != options.start.decode("utf8"):
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
	print nr

if __name__ == "__main__":
	main()

