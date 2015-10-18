#!/usr/bin/python
# -*- coding: utf8 -*-

import re
from Page import *

class NounIterator(object):
	def __init__(self, start = None):
		self.start = start
		self.idx = 0
		self.started = False

	def filtered(self, n):
		if self.started:
			return False
		#print "%s %s" % (n, self.start)
		if self.start is None or n == self.start:
			self.started = True
			return False
		return True

	def __iter__(self):
		return self

	def next(self):
		n = self._next()
		while self.filtered(n):
			n = self._next()
		return n

class NounPageIterator(NounIterator):
	def _next(self):
		while self.idx >= len(self.it.nouns):
			self.it = self.it.next()
			self.idx = 0

		nouns = self.it.nouns
		n = nouns[self.idx]
		self.idx += 1
		return n

class GermanNounPageIterator(NounPageIterator):
	URL = "http://de.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Kategorie:Substantiv_(Deutsch)&format=json"

	def __iter__(self):
		self.it = NounListPage(self.URL)
		return NounPageIterator.__iter__(self)

	def next(self):
		n = NounPageIterator.next(self)
		return GermanNounPage.from_noun(n)

class GermanNounPageRawIterator(NounPageIterator):
	URL = "http://de.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=%s&format=json"

	def __init__(self, cat, start = None):
		#@cat = ex: Kategorie:Substantiv_(Deutsch)
		self.url = self.URL % cat
		NounPageIterator.__init__(self, start)
		
	def __iter__(self):
		self.it = NounListPage(self.url)
		return NounPageIterator.__iter__(self)

class EnglishNounPageIterator(NounPageIterator):
	URL = "http://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:English_adjectives&format=json"

	def __iter__(self):
		self.it = EnglishNounListPage(self.URL)
		return NounPageIterator.__iter__(self)

	def next(self):
		n = NounPageIterator.next(self)
		return EnglishNounPage.from_noun(n)

class NounFileIterator(NounIterator):
	def __init__(self, f, start = None):
		NounIterator.__init__(self, start)
		self.file = f
		self.fp = open(f, "r")

	def __iter__(self):
		NounIterator.__iter__(self)
		self.it = iter(self.fp)
		return self

	def _next(self):
		return self.it.next().strip().decode("utf-8")

class GermanNounFileIterator(NounFileIterator):
	def next(self):
		n = NounFileIterator.next(self)
		return GermanNounPage.from_noun(n)

class FreqNounIterator(NounPageIterator):
	URL = "http://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=%s&format=json"

	def __init__(self, title):
		"ex: Wiktionnaire:Listes_de_fréquence/wortschatz-de-1-2000"
		self.page = FrenchNounPage.from_noun(title)
		
	def __iter__(self):
		self.it = iter(self.page.wikicode().splitlines())
		self.remain = None
		return self

	def next(self):
		if self.remain is not None:
			r = self.remain
			self.remain = None
			return r

		while True:
			line = self.it.next()
			s = re.search("[*] [0-9]+[.] [[]{2}(.+?)[]]{2}", line)
			if s is not None:
				g = s.group(1)
				g = g.split("|")
				if len(g) > 1:
					self.remain = g[1]
				return g[0]

class CategoryRawIterator(NounPageIterator):
	URL = u"http://%s.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=%s:%s&format=json&cmlimit=500"

	def __init__(self, dom, catword, cat, start):
		self.url = self.URL % (dom, catword, cat)
		NounPageIterator.__init__(self, start)
		
	def __iter__(self):
		self.it = NounListPage(self.url)
		return NounPageIterator.__iter__(self)

class FrenchCategoryRawIterator(CategoryRawIterator):
	def __init__(self, cat, start = None):
		#@cat = ex: "Noms communs en français")
		return CategoryRawIterator.__init__(self, u"fr", u"Catégorie", cat, start)

class SpanishCategoryRawIterator(CategoryRawIterator):
	def __init__(self, cat, start = None):
		#@cat = ex: "Noms communs en français")
		return CategoryRawIterator.__init__(self, u"es", u"Categoría", cat, start)

class RecentChangesIterator(NounPageIterator):
	def __init__(self, rcstart = None, until = None, domain = "fr"):
		NounPageIterator.__init__(self)
		self.rcstart = rcstart
		self.until = until
		self.domain = domain

	def __iter__(self):
		self.it = RecentChangesPage(rcstart = self.rcstart, until = self.until, domain = self.domain)
		return NounPageIterator.__iter__(self)

class SearchIterator(NounPageIterator):
	def __init__(self, search):
		NounPageIterator.__init__(self)
		self.search = search

	def __iter__(self):
		self.it = SearchPage(self.search)
		return NounPageIterator.__iter__(self)
