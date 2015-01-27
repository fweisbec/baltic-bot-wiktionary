#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, requests, time
from threading import Thread
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

DOMS = ("af", "an", "ar", "ast", "az", \
		"be", "bg", "br", "bs", \
		"ca", "chr", "co", "cs", "csb", "cy", \
		"da", "de", \
		"el", "en", "eo", "es", "et", "eu", \
		"fa", "fi", "fj", "fy", \
		"ga", "gl", "gu", \
		"he", "hi", "hr", "hsb", "hu", "hy", \
		"id", "io", "is", "it", \
		"ja", "jv", \
		"ka", "kk", "kl", "km", "kn", "ko", "ku", "ky", \
		"la", "lb", "li", "ln", "lo", "lt", "lv", \
		"mg", "mk", "ml", "mn", "mr", "ms", "mt", "my", \
		"nah", "nds", "nl", "nn", "no", \
		"oc", "om", \
		"pl", "pt", \
		"ro", "ru", "rw", \
		"sa", "scn", "sh", "simple", "sk", "sl", "sm", "sq", "sr", "ss", "st", "sv", "sw", \
		"ta", "te", "th", "tk", "tl", "tpi", "tr", "tt", \
		"ug", "uk", "uz", \
		"vec", "vi", "vo", \
		"wa", \
		"yi", \
		"zh", "zh-min-nan", "zu")

def diff_auto_accept(word, diff):
	empty = 0
	interlinks = False
	for line in diff.splitlines():
		if line.startswith(("---", "+++")):
			continue
		if line.startswith("-"):
			return False
		if line.startswith("+"):
			# One empty line above interlinks
			if line == "+":
				empty += 1
				if empty > 1:
					return False
				if interlinks:
					return False
				continue
			# Interlink
			m = re.match(u"\+\[\[[a-z-]+:%s\]\]" % word, line, re.U)
			if m is None:
				return False
			else:
				interlinks = True
	return True

def update_doms(word, doms):
	e = Editor(word)
	e.update_doms(doms)
	diff = e.diff()

	if not diff:
		print colored("No change, skipping...", "red")
		return
	if diff_auto_accept(word, diff):
		e.commit(u"Update liens externes")
		print colored("Automatically committed!", "green")
		log = open("interlink_auto.log", "a")
		log.write("\n" + diff.encode("utf-8"))
		log.close()
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
		self.error = False

	def run(self):
		try:
			p = NounPage.from_noun_dom(self.word, self.dom)
		except requests.ConnectionError:
			self.error = True
			return
		if p.valid():
			self.has_page = True

def get_doms_async(word):
	doms = []
	threads = []
	WiktionaryCookie.WiktionaryCookie.set_anon_mode()
	sys.stdout.write(word + " " * (50 - len(word)))
	sys.stdout.flush()
	for dom in DOMS:
		t = GetDomThread(dom, word)
		threads.append(t)
		t.start()

	for t in threads:
		t.join()
		if t.error:
			raise requests.ConnectionError
		if t.has_page:
			doms.append(t.dom)
	WiktionaryCookie.WiktionaryCookie.clear_anon_mode()
	return doms

def main():
	start = None
	if len(sys.argv) > 1:
		start = sys.argv[1].decode("utf8")
	it = FrenchCategoryRawIterator(u"letton", start = start)
	for i in it:
		if "," in i:
			continue
		while True:
			try:
				doms = get_doms_async(i)
				break
			except requests.ConnectionError:
				print "Error, retrying..."
				time.sleep(1)
		if doms:
			update_doms(i, doms)
		else:
			print colored("No interlink", "red")
		

if __name__ == "__main__":
	main()
