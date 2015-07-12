#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, requests, time, optparse, exceptions
from threading import Thread
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

DOMS = ("af", "am", "an", "ang", "ar", "ast", "ay", "az", \
		"be", "bg", "bn", "br", "bs", \
		"ca", "chr", "co", "cs", "csb", "cy", \
		"da", "de", "dv", \
		"el", "en", "eo", "es", "et", "eu", \
		"fa", "fi", "fj", "fo", "fy", \
		"ga", "gd", "gl", "gn", "gu", "gv", \
		"ha", "he", "hi", "hr", "hsb", "hu", "hy", \
		"ia", "id", "ie", "ik", "io", "is", "it", "iu", \
		"ja", "jbo", "jv", \
		"ka", "kk", "kl", "km", "kn", "ko", "ks", "ku", "kw", "ky", \
		"la", "lb", "li", "ln", "lo", "lt", "lv", \
		"mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", \
		"na", "nah", "nds", "ne", "nl", "nn", "no", \
		"oc", "om", "or", \
		"pa", "pl", "pnb", "ps", "pt", \
		"qu", \
		"ro", "roa-rup", "ru", "rw", \
		"sa", "scn", "sd", "sg", "sh", "si", "simple", "sk", "sl", "sm", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", \
		"ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "tpi", "tr", "ts", "tt", \
		"ug", "uk", "ur", "uz", \
		"vec", "vi", "vo", \
		"wa", "wo", \
		"yi", \
		"za", "zh", "zh-min-nan", "zu")

parser = optparse.OptionParser()
parser.add_option("-c", "--category", type = "string", dest = "cat", default = None)
parser.add_option("-i", "--input", type = "string", dest = "input", default = None)
parser.add_option("-r", "--recent-changes", type = "string", dest = "recent_changes_until", default = None) # ex: 2015-02-01T00:00:00Z
parser.add_option("-d", "--domain", type = "string", dest = "domain", default = "fr") # domain from recent changes
parser.add_option("-m", "--manual", type = "string", dest = "manual", default = "interlink_manual.log")
parser.add_option("-s", "--start", type = "string", dest = "start", default = None)
parser.add_option("-a", "--auto", action = "store_true", dest = "auto")
parser.add_option("-f", "--force", action = "store_true", dest = "force")
parser.add_option("-n", "--number", type = "int", dest = "number", default = 50)
(options, args) = parser.parse_args()

def diff_ignore(diff):
	if not diff:
		return True

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

	# Alias interlink need manual check
	s = re.search(u"\[\[[a-z-]+:((?!%s)|(%s.+)).*\]\]" % (word, word), diff, re.U)
	if s is not None:
		return False

	plus = []
	minus = []
	for line in diff.splitlines():
		if line.startswith(("---", "+++")):
			continue
		if line.startswith("-"):
			minus.append(line[1:].rstrip())
		if line.startswith("+"):
			plus.append(line[1:].rstrip())

	check_mirrored = []
	has_interlinks = False
	for line in minus:
		# Empty line
		if not line.strip():
			continue
		# Interlink
		m = re.match(u"\[\[[a-z-]+:%s\]\]" % word, line, re.U)
		if m is not None:
			has_interlinks = True
		if line in plus:	
			plus.remove(line)
		else:
			return False

	for line in plus:
		# Empty line
		if not line.strip():
			continue
		# Only allow interlinks
		m = re.match(u"\[\[[a-z-]+:%s\]\]" % word, line, re.U)
		if m is None:
			return False
		has_interlinks = True

	return has_interlinks


def commit(editor):
	delay = 5
	while True:
		try:
			editor.commit(u"Update liens interwikis")
			break
		except requests.RequestException as e:
			print colored(repr(e), "red")
			print colored(" retrying in %d" % delay, "red")
			time.sleep(delay)
			delay *= 2
		

def update_word_doms(word, wikicode, basetimestamp, doms):
	e = Editor(word, wikicode, basetimestamp)
	e.update_doms(doms)
	diff = e.diff()

	# Skip empty diff
	if diff_ignore(diff):
		print colored("No change, skipping...", "blue")
		return

	# Auto commit trivial case
	if diff_auto_accept(word, diff):
		commit(e)
		print colored("Automatically committed!", "green")
		log = open("interlink_auto.log", "a")
		log.write("\n" + diff.encode("utf-8"))
		log.close()
		return

	# Log non-trivial cases
	if not options.force and options.auto:
		log = open(options.manual, "a")
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
		delay = 5
                commit(e)
                print "Committed!"
	else:
		print "?"

def update_words_doms(words_doms):
	words = words_doms.keys()
	if not words:
		return

	# Load words pages from fr.wiktionary
	delay = 5
	while True:
		t = time.time()
		sys.stdout.write(colored("Loading %d words from fr..." % len(words), "yellow"))
		try:
			pages = NounPage.from_nouns_dom(words, "fr")
			if pages.error():
				print colored(pages.error(), "red")
			else:
				print colored(" completed in %f" % (time.time() - t), "yellow")
				break
		except requests.RequestException as e:
			print colored(repr(e), "red")

		print colored(" retrying in %d" % delay, "red")
		time.sleep(delay)
		delay *= 2

	# Update each word with uptodate doms
	for w in words:
		sys.stdout.write(w + " " * (50 - len(w)))
		delay = 5
		while True:
			try:
				key = pages.key(w)
				if key is None:
					print colored("Unable to find key for %s" % w, "red")
					sys.exit(-1)
				if not pages.valid(key):
					if pages.missing(key):
						print colored("Missing page for %s" % w, "red")
						break
					elif pages.invalid(key):
						print colored("Invalid page for %s" % w, "red")
					else:
						print colored("Weird page for %s" % w, "red")
					sys.exit(-1)
				wikicode = pages.wikicode(key)
				basetimestamp = pages.revision_time(key) 
				update_word_doms(w, wikicode, basetimestamp, words_doms[w])
				break
			except requests.RequestException as e:
				print colored("Unable to commit edit, %s" % repr(e), "red")
				time.sleep(delay)
				delay *= 2

class GetDomWordsThread(Thread):
	def __init__(self, dom, words):
		Thread.__init__(self)
		self.dom = dom
		self.words = words
		self.error_msg = None
		self.page = None

	def run(self):
		try:
			p = TestPage.from_nouns_dom(self.words, self.dom)
		except requests.RequestException as e:
			self.error_msg = repr(e)
			return
		# Error such as maxlag
		if p.error():
			self.error_msg = p.error()
		else:
			self.page = p

def get_doms_pages(words):
	doms_pages = []
	threads = []
	WiktionaryCookie.WiktionaryCookie.set_anon_mode()
	for dom in DOMS:
		t = GetDomWordsThread(dom, words)
		threads.append(t)
		t.start()

	for t in threads:
		t.join()
		if not t.page:
			sys.stdout.write(colored("Dom %s Error %s" % (t.dom, t.error_msg), "red"))
			raise requests.ConnectionError
		doms_pages.append(t.page)
	WiktionaryCookie.WiktionaryCookie.clear_anon_mode()
	return doms_pages

def iterate_words(words):
	delay = 5
	doms_words = []
	# Fetch words per dom
	while True:
		sys.stdout.write(colored("Loading %d words from external doms..." % len(words), "yellow"))
		sys.stdout.flush()
		t = time.time()
		try:
			doms_pages = get_doms_pages(words)
			print colored(" completed in %f" % (time.time() - t), "yellow")
			break
		except requests.RequestException:
			print colored(" retrying in %d" % delay, "red")
			time.sleep(delay)
			delay *= 2

	# Store doms per words in a dict
	i = 0
	words_doms = {}
	for w in words:
		words_doms[w] = []
		for dom_pages in doms_pages:
			key = dom_pages.key(w)
			if key is None:
				dom_pages.debug(w)
				print dom_pages.json
			if dom_pages.valid(key):
				words_doms[w].append(dom_pages.dom)
		if not words_doms[w]:
			sys.stdout.write(w + " " * (50 - len(w)))
			print colored("No interlink", "blue")
			del words_doms[w]

	# Update doms for words that need it
	update_words_doms(words_doms)

def iterate(it):
	nr = 0
	words = []
	for i in it:
		if not i or "," in i or "+" in i or "*" in i or "?" in i or "\\" in i:
			continue
		if nr == options.number:
			iterate_words(words)
			words = []
			nr = 0
			#time.sleep(10)
		words.append(i)
		nr += 1
	# Less than options.number words remaining, flush them
	if words:
		iterate_words(words)

def main():
	start = None
	if options.start:
		start = options.start.decode("utf-8")
	if options.input:
		it = NounFileIterator(options.input, start)
	elif options.cat:
		it = FrenchCategoryRawIterator(options.cat.decode("utf-8"), start = start)
	elif options.recent_changes_until:
		it = RecentChangesIterator(start = start, until = options.recent_changes_until.decode("utf-8"), domain = options.domain)
	else:
		print "Need either -i, -c or -r"
		sys.exit(-1)

	iterate(it)

if __name__ == "__main__":
	main()
