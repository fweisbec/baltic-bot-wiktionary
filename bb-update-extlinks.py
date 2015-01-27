#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, requests
from threading import Thread

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

DOMS = ("af", "an", "ar", "ast", "az", \
		"be", "bg", "br", "bs", \
		"ca", "chr", "cs", "csb", "cy", \
		"da", "de", \
		"el", "en", "eo", "es", "et", "eu", \
		"fa", "fi", "fj", "fy", \
		"gl", "gu", \
		"he", "hi", "hr", "hsb", "hu", "hy", \
		"id", "io", "is", "it", \
		"ja", \
		"kk", "kn", "ko", "ku", "ky", \
		"la", "lb", "li", "lo", "lt", "lv", \
		"mg", "mk", "ml", "mr", "my", \
		"nl", "nn", "no", \
		"oc", \
		"pl", "pt", \
		"ro", "ru", \
		"sa", "scn", "sh", "simple", "sk", "sl", "sm", "sq", "sr", "sv", "sw", \
		"ta", "te", "th", "tk", "tl", "tr", \
		"uk", "uz", \
		"vec", "vi", \
		"yi", \
		"zh")

def update_doms(word, doms):
	e = Editor(word)
	e.update_doms(doms)
	diff = e.diff()
	if not diff:
		print "No change, skipping..."
		return
	print diff
	accept = raw_input("Commit change? (Y/n) ")
	if accept == "n":
		return
	elif not accept or accept in ("y", "Y"):
		e.commit(u"Update liens externes")
		print "Committed!"
	else:
		print "?"

class GetDomThread(Thread):
	def __init__(self, dom, word):
		Thread.__init__(self)
		self.dom = dom
		self.word = word
		self.has_page = False

	def run(self):
		p = NounPage.from_noun_dom(self.word, self.dom)
		if p.valid():
			self.has_page = True

def get_doms_async(word):
	doms = []
	threads = []
	WiktionaryCookie.WiktionaryCookie.set_anon_mode()
	print word
	for dom in DOMS:
		t = GetDomThread(dom, word)
		threads.append(t)
		t.start()

	for t in threads:
		t.join()
		if t.has_page:
			doms.append(t.dom)
	WiktionaryCookie.WiktionaryCookie.clear_anon_mode()
	return doms

def get_doms_sync(word):
	doms = []
	raw = word.encode("utf8")
	for dom in DOMS:
		sys.stdout.write(" " * 70)
		sys.stdout.write("\r")
		sys.stdout.write(raw + " " * (50 - len(word)) + dom)
		sys.stdout.flush()
		p = NounPage.from_noun_dom(word, dom)
		if p.valid():
			doms.append(dom)
	sys.stdout.write("\n")
	return doms

def main():
	start = None
	if len(sys.argv) > 1:
		start = sys.argv[1].decode("utf8")
	it = FrenchCategoryRawIterator(u"Noms communs en letton", start = start)
	for i in it:
		doms = get_doms_async(i)
		if doms:
			update_doms(i, doms)
		

if __name__ == "__main__":
	main()
