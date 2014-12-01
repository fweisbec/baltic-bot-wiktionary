#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, urllib, re
import WiktionaryCookie

class JsonPage(object):
	def __init__(self, url):
		self.url = url
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		self.req = requests.get(url, cookies = cookies)
		try:
			self.json = self.req.json()
		except ValueError:
			print self.url
			print "No json: %s" % self.req.text
			raise ValueError
		cookies.update(self.req.cookies)

class RevisionFrenchPage(JsonPage):
	URL = "http://fr.wiktionary.org/w/api.php?format=json&action=query&%s&prop=revisions&rvprop=timestamp"

	@classmethod
	def from_noun(cls, noun):
		url = cls.URL % urllib.urlencode({"titles" : noun.encode("utf-8") })
		return cls(url)

	def revision_time(self):
		return self.json["query"]["pages"].values()[0]["revisions"][0]["timestamp"]

class NounPage(JsonPage):
	@classmethod
	def from_noun(cls, noun):
		base_url = "http://" + cls.DOM + ".wiktionary.org/w/api.php?format=json&action=query&%s&prop=revisions&rvprop=content"
		url = base_url % urllib.urlencode({"titles" : noun.encode("utf-8") })
		return cls(noun, url)
		
	def __init__(self, noun, url):
		JsonPage.__init__(self, url)
		self.noun = noun

	def valid(self):
		status = self.json["query"]["pages"].values()[0]
		for i in ("missing", "invalid"):
			if i in status:
				return False
		return True

	def wikicode(self):
		return self.json["query"]["pages"].values()[0]["revisions"][0]["*"].encode("utf-8")

	def _get_translations(self, reg):
		res = re.findall(reg, self.wikicode(), re.M)
		return [r.decode("utf-8") for r in res]

class FrenchNounPage(NounPage):
	DOM = "fr"

	def get_english(self):
		return self._get_translations("\{\{trad[+-]\|en\|(.+?)\}\}")

	def get_german(self):
		return self._get_translations("\{\{trad[+-]\|de\|(.+?)\}\}")

	def find_l4_section(self, s):
		return self.wikicode().find(pattern % s)

class EnglishNounPage(NounPage):
	DOM = "en"

	def get_french(self):
		return self._get_translations("\{\{t[+-]\|fr\|(.+?)(?:\|.+)?\}\}")

class GermanNounPage(NounPage):
	DOM = "de"

	def get_french(self):
		return self._get_translations("\{\{Ü\|fr\|(.+?)(?:\|.+)?\}\}")
		 

class NounListPage(JsonPage):
	def __init__(self, url):
		JsonPage.__init__(self, url)
		members = self.json["query"]["categorymembers"]			
		self.nouns = [m["title"] for m in members if not self._filter_link(m["title"])]

	def next(self):
		cont = self.json["query-continue"]["categorymembers"]["cmcontinue"]
		url = self.url.split("&cmcontinue=")[0]
		url = "%s&cmcontinue=%s" % (url, cont)
		return self.__class__(url)
	
class EnglishNounListPage(NounListPage):
	def _filter_link(self, links):
		if links.startswith(("Category:", "Wiktionary:", "Special:", "Category_talk:", "Appendix:")):
			return True
		return False

class GermanNounListPage(NounListPage):
	def _filter_link(self, links):
		return False

class FrenchCategoryPage(NounListPage):
	def _filter_link(self, links):
		return False
