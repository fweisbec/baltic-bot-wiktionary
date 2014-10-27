#!/usr/bin/python
# -*- coding: utf8 -*-

from Page import *

class NounIterator(object):
	def __init__(self, start):
		self.start = start

	def filtered(self, n):
		if self.started:
			return False
		#print "%s %s" % (n, self.start)
		if n == self.start:
			self.started = True
			return False
		return True

	def __iter__(self):
		self.idx = 0
		self.started = False
		return self

	def next(self):
		n = self._next()
		while self.filtered(n):
			n = self._next()
		return n

class NounPageIterator(NounIterator):
	def _next(self):
		if self.idx >= len(self.it.nouns):
			self.it = self.it.next()
			self.idx = 0
			#assert len(self.it.nouns) == 0

		nouns = self.it.nouns
		n = nouns[self.idx]
		self.idx += 1
		return n

class GermanNounPageIterator(NounPageIterator):
	URL = "http://de.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Kategorie:Substantiv_(Deutsch)&format=json"

	def __iter__(self):
		self.it = GermanNounListPage(self.URL)
		return NounPageIterator.__iter__(self)

	def next(self):
		n = NounPageIterator.next(self)
		return GermanNounPage.from_noun(n)

class GermanNounPageRawIterator(NounPageIterator):
	URL = "http://de.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Kategorie:Substantiv_(Deutsch)&format=json"

	def __iter__(self):
		self.it = GermanNounListPage(self.URL)
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
	def __init__(self, start, f):
		NounIterator.__init__(self, start)
		self.file = f
		self.fp = open(f, "r")

	def __iter__(self):
		NounIterator.__iter__(self)
		self.it = iter(self.fp)
		return self

	def _next(self):
		return self.it.next().strip()

class GermanNounFileIterator(NounFileIterator):
	def next(self):
		n = NounFileIterator.next(self)
		return GermanNounPage.from_noun(n.decode("utf-8"))
