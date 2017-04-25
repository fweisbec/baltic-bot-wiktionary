#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, requests, time, optparse, exceptions, math
from threading import Thread
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

DOMS = ("aa", "ab", "af", "ak", "als", "am", "an", "ang", "ar", "as", "ast", "av", "ay", "az", \
		"be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs", \
		"ca", "ch", "chr", "co", "cr", "cs", "csb", "cy", \
		"da", "de", "dv", "dz", \
		"el", "en", "eo", "es", "et", "eu", \
		"fa", "fi", "fj", "fo", "fy", \
		"ga", "gd", "gl", "gn", "gu", "gv", \
		"ha", "he", "hi", "hr", "hsb", "hu", "hy", \
		"ia", "id", "ie", "ik", "io", "is", "it", "iu", \
		"ja", "jbo", "jv", \
		"ka", "kk", "kl", "km", "kn", "ko", "ks", "ku", "kw", "ky", \
		"la", "lb", "li", "ln", "lo", "lt", "lv", \
		"mg", "mh", "mi", "mk", "ml", "mn", "mo", "mr", "ms", "mt", "my", \
		"na", "nah", "nds", "ne", "nl", "nn", "no", \
		"oc", "om", "or", \
		"pa", "pi", "pl", "pnb", "ps", "pt", \
		"qu", \
		"rm", "rn", "ro", "roa-rup", "ru", "rw", \
		"sa", "sc", "scn", "sd", "sg", "sh", "si", "simple", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", \
		"ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tpi", "tr", "ts", "tt", "tw", \
		"ug", "uk", "ur", "uz", \
		"vec", "vi", "vo", \
		"wa", "wo", \
		"xh", \
		"yi", "yo", \
		"za", "zh", "zh-min-nan", "zu")

parser = optparse.OptionParser()
parser.add_option("-c", "--category", type = "string", dest = "cat", default = None)
parser.add_option("-i", "--input", type = "string", dest = "input", default = None)
parser.add_option("-r", "--recent-changes", type = "string", dest = "recent_changes_until") # 2000-01-01T00:00:00Z
parser.add_option("-m", "--manual", type = "string", dest = "manual", default = "interlink_manual.log")
parser.add_option("-s", "--start", type = "string", dest = "start", default = None)
parser.add_option("-a", "--auto", action = "store_true", dest = "auto")
parser.add_option("-f", "--force", action = "store_true", dest = "force")
parser.add_option("--dry-run", action = "store_true", dest = "dry_run")
(options, args) = parser.parse_args()

def enc(s):
	return s.encode("utf8")

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

def diff_auto_accept(editor):
	if options.force:
		return False

	spl = editor.old.rstrip().split(editor.new)
	if len(spl) > 2:
		return False
	if spl[0] != "":
		return False
	return True

def build_summary(word, editor):
	return u"Retrait des liens interlangues qui sont maintenant gérés automatiquement par [[mw:Extension:Cognate]]."

def commit(word, editor):
	delay = 5
	summary = build_summary(word, editor)
	while True:
		try:
			if not options.dry_run:
				editor.commit(summary, minor = True)
			break
		except requests.RequestException as e:
			print colored(repr(e), "red")
			print colored(" retrying in %d" % delay, "red")
			time.sleep(delay)
			delay *= 2
		

def update_word(word, wikicode, basetimestamp):
	e = Editor(word, wikicode, basetimestamp)
	e.suppr_doms(DOMS)
	diff = e.diff()

	# Skip empty diff
	if diff_ignore(diff):
		print colored("No change, skipping...", "blue")
		return

	# Auto commit trivial case
	if diff_auto_accept(e):
		commit(word, e)
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
                commit(word, e)
                print "Committed!"
	else:
		print "?"

def update_words(words):
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
		sys.stdout.write(enc(w) + " " * (50 - len(w)))
		delay = 5
		while True:
			try:
				key = pages.key(w)
				if key is None:
					print colored("Unable to find key for %s" % enc(w), "red")
					sys.exit(-1)
				if not pages.valid(key):
					if pages.missing(key):
						print colored("Missing page for %s" % enc(w), "red")
						break
					elif pages.invalid(key):
						print colored("Invalid page for %s" % enc(w), "red")
					else:
						print colored("Weird page for %s" % enc(w), "red")
					sys.exit(-1)
				wikicode = pages.wikicode(key)
				basetimestamp = pages.revision_time(key) 
				update_word(w, wikicode, basetimestamp)
				break
			except requests.RequestException as e:
				print colored("Unable to commit edit, %s" % repr(e), "red")
				time.sleep(delay)
				delay *= 2

	return True

def iterate_words(words, nr):
	length = len(words)
	# Often too many words produce URL too longs.
	# On such case, to a dichotomic iteration
	if nr >= length:
		if update_words(words):
			return min(nr + 1, 50)
		else:
			assert(length > 1)
			nr = math.ceil(nr / 2.0)

	nr = iterate_words(words[:length/2], nr)
	nr = iterate_words(words[length/2:], nr)
	return nr

def iterate(it, number):
	nr = 0
	words = []
	for i in it:
		if not i or "," in i or "+" in i or "*" in i or "?" in i or "\\" in i:
			continue
		if nr == number:
			number = iterate_words(words, number)
			words = []
			nr = 0
		words.append(i)
		nr += 1
	# Less than @number words remaining, flush them
	if words:
		iterate_words(words, number)

def main():
	start = None
	if options.start:
		start = options.start.decode("utf-8")
	if options.input:
		it = NounFileNameIterator(options.input, start)
	elif options.cat:
		it = FrenchCategoryRawIterator(options.cat.decode("utf-8"), start = start)
	elif options.recent_changes_until:
		it = RecentChangesIterator(rcstart = start, until = options.recent_changes_until.decode("utf-8"), domain = "fr")
	else:
		print "Need either -i, -c or -r"
		sys.exit(-1)

	iterate(it, 50)

if __name__ == "__main__":
	main()
