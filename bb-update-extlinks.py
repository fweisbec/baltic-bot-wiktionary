#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, requests, time, optparse
from threading import Thread
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

DOMS = ("af", "am", "an", "ang", "ar", "ast", "az", \
		"be", "bg", "bn", "br", "bs", \
		"ca", "chr", "co", "cs", "csb", "cy", \
		"da", "de", "dv", \
		"el", "en", "eo", "es", "et", "eu", \
		"fa", "fi", "fj", "fo", "fy", \
		"ga", "gl", "gn", "gu", \
		"he", "hi", "hr", "hsb", "hu", "hy", \
		"ia", "id", "ie", "ik", "io", "is", "it", \
		"ja", "jbo", "jv", \
		"ka", "kk", "kl", "km", "kn", "ko", "ku", "kw", "ky", \
		"la", "lb", "li", "ln", "lo", "lt", "lv", \
		"mg", "mk", "ml", "mn", "mr", "ms", "mt", "my", \
		"na", "nah", "nds", "ne", "nl", "nn", "no", \
		"oc", "om", \
		"pl", "pnb", "ps", "pt", \
		"ro", "roa-rup", "ru", "rw", \
		"sa", "scn", "sd", "sg", "sh", "si", "simple", "sk", "sl", "sm", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", \
		"ta", "te", "tg", "th", "tk", "tl", "tpi", "tr", "tt", \
		"ug", "uk", "ur", "uz", \
		"vec", "vi", "vo", \
		"wa", "wo", \
		"yi", \
		"zh", "zh-min-nan", "zu")

parser = optparse.OptionParser()
parser.add_option("-c", "--category", type = "string", dest = "cat", default = "letton")
parser.add_option("-s", "--start", type = "string", dest = "start", default = None)
parser.add_option("-a", "--auto", action = "store_true", dest = "auto")
parser.add_option("-f", "--force", action = "store_true", dest = "force")
(options, args) = parser.parse_args()

def diff_ignore(diff):
	if options.force:
		return False

	if not diff:
		return True

	moins = 0
	for line in diff.splitlines():
		if line.startswith(("---", "+++")):
			continue
		if line.startswith(("+", "-")):
			if len(line.rstrip()) > 1:
				return False
	# If no add and no sub (except empty lines), change isn't worth
	return True

def diff_auto_accept(word, diff):
	if options.force:
		return False
	empty = 0
	interlinks = False
	for line in diff.splitlines():
		if line.startswith(("---", "+++")):
			continue
		if line.startswith("-"):
			return False
		if line.startswith("+"):
			# One empty line above interlinks
			if line.rstrip() == "+":
				empty += 1
				# No more than one empty line
				if empty > 1:
					return False
				# No empty line after interlinks
				if interlinks:
					return False
				continue
			# Interlink
			m = re.match(u"\+\[\[[a-z-]+:%s\]\]" % word, line, re.U)
			if m is None:
				return False
			else:
				interlinks = True

	if empty > 0 and not interlinks:
		return False

	return True

def update_doms(word, doms):
	e = Editor(word)
	e.update_doms(doms)
	diff = e.diff()

	# Skip empty diff
	if diff_ignore(diff):
		print colored("No change, skipping...", "blue")
		return

	# Auto commit trivial case
	if diff_auto_accept(word, diff):
		e.commit(u"Update liens interwikis")
		print colored("Automatically committed!", "green")
		log = open("interlink_auto.log", "a")
		log.write("\n" + diff.encode("utf-8"))
		log.close()
		return

	# Log non-trivial cases
	if not options.force and options.auto:
		log = open("interlink_manual.log", "a")
		print colored("Non trivial change: logged", "magenta")
		log.write("\n" + word.encode("utf-8"))
		log.close()
		return

	# Or handle non-trivial case now
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
		self.error_msg = None

	def run(self):
		try:
			p = TestPage.from_noun_dom(self.word, self.dom)
		except requests.ConnectionError:
			self.error = True
			self.error_msg = "requests.ConnectionError"
			return
		# Error such as maxlag
		if p.error():
			self.error = True
			self.error_msg = p.error()
		elif p.valid():
			self.has_page = True

def get_doms_async(word):
	doms = []
	threads = []
	WiktionaryCookie.WiktionaryCookie.set_anon_mode()
	sys.stdout.write(word + " " * (50 - len(word)))
	sys.stdout.flush()
	#ti = time.time()
	for dom in DOMS:
		t = GetDomThread(dom, word)
		threads.append(t)
		t.start()

	for t in threads:
		t.join()
		if t.error:
			sys.stdout.write(colored("Error %s" % t.error_msg, "red"))
			raise requests.ConnectionError
		if t.has_page:
			doms.append(t.dom)
	#print time.time() - ti
	WiktionaryCookie.WiktionaryCookie.clear_anon_mode()
	return doms

def iterate(it):
	for i in it:
		if "," in i:
			continue
		delay = 5
		while True:
			try:
				doms = get_doms_async(i)
				break
			except requests.ConnectionError:
				print colored(" retrying in %d" % delay, "red")
				time.sleep(delay)
				delay *= 2
		if doms:
			update_doms(i, doms)
		else:
			print colored("No interlink", "blue")

def main():
	#w = WiktionaryCookie.WiktionaryCookie()
	#w.logout()
	start = None
	if options.start:
		start = options.start.decode("utf-8")
	it = FrenchCategoryRawIterator(options.cat.decode("utf-8"), start = start)
	iterate(it)

if __name__ == "__main__":
	main()
