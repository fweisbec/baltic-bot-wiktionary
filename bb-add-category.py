#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *


parser = optparse.OptionParser()
parser.add_option("-c", "--category", type = "string", dest = "category")
parser.add_option("-i", "--input", type = "string", dest = "input")
(options, args) = parser.parse_args()

nr_commits = 0

def commit(e, diff):
	summary = "Ajout catégorie verbe irrégulier en espagnol"
	e.commit(summary)
	fp = open("commits.log", "a")
	fp.write("---------\n")
	fp.write(diff.encode("utf8"))
	fp.close()
	global nr_commits
	nr_commits += 1

nr = 0
def process_one(p, title):
	global nr, nr_commits
	nr+=1
	key = p.key(title)
	wikicode = p.wikicode(key)
	basetimestamp = p.revision_time(key)
	e = Editor(title, wikicode, basetimestamp)
	if not e.add_category(options.category.decode("utf8")):
		return False
	diff = e.diff()
	if not diff:
		return False
	return True
	print diff
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return False
	elif not accept or accept in ("y", "Y"):
		commit(e, diff)
		return True
	else:
		print "?"
	return False

def process_titles(titles):
	sys.stdout.write(colored("Loading 50 words from search\n", "yellow"))
	p = NounPage.from_nouns_dom(titles, "fr")
	for title in titles:
		sys.stdout.write(title.encode("utf8") + " " * (50 - len(title)))
		key = p.key(title)
		if not p.valid(key):
			print colored("Not found", "red")
			continue
		committed = False
		res = process_one(p, title)
		if res:
			committed = True
		if not committed:
			print colored("No change", "blue")
		else:
			global nr_commits
			print colored("Committed (%d)" % nr_commits, "green")

def main():
	it = NounFileNameIterator(options.input)

	titles = []
	for i in it:
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

