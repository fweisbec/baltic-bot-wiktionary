#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, urllib, re
import WiktionaryCookie

class JsonPage(object):
	def __init__(self, url, dom = None):
		self.url = url
		self.dom = dom
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		headers = {"User-Agent" : "Baltic Bot (https://fr.wiktionary.org/wiki/Utilisateur:Baltic_Bot ; fweisbec@gmail.com)"}
		self.req = requests.get(url, cookies = cookies, headers = headers)
		if self.req.status_code != requests.codes.ok:
			self.req.raise_for_status()
		try:
			self.json = self.req.json()
		except ValueError:
			print self.url
			print "No json: %s" % self.req.text
			raise ValueError
		cookies.update(self.req.cookies)

	def error(self):
		if "error" in self.json:
			return self.json["error"]["code"]
		return None

class QueryPage(JsonPage):
	def __init__(self, noun, url, dom = None):
		url += "&maxlag=5"
		JsonPage.__init__(self, url, dom)
		self.noun = noun

	def key(self, title):
		for k in self.json["query"]["pages"]:
			if title == self.json["query"]["pages"][k]["title"]:
				return k
		return None
			
	def title(self, key):
		return self.json["query"]["pages"][key]["title"]

	def valid(self, key):
		status = self.json["query"]["pages"][key]
		for i in ("missing", "invalid"):
			if i in status:
				return False
		return True

class TestPage(QueryPage):
	@classmethod
	def from_nouns_dom(cls, nouns, dom):
		base_url = "http://" + dom + ".wiktionary.org/w/api.php?format=json&action=query&titles=%s"
		http_nouns = "|".join([urllib.quote_plus(noun.encode("utf8")) for noun in nouns])
		url = base_url % http_nouns 
		return cls(noun, url, dom)

class NounPage(QueryPage):
	@classmethod
	def from_nouns_dom(cls, nouns, dom):
		base_url = "http://" + dom + ".wiktionary.org/w/api.php?format=json&action=query&titles=%s&prop=revisions&rvprop=content|timestamp"
		http_nouns = "|".join([urllib.quote_plus(noun.encode("utf8")) for noun in nouns])
		url = base_url % http_nouns 
		return cls(noun, url, dom)

	@classmethod
	def from_noun_dom(cls, noun, dom):
		return cls.from_nouns_dom([noun], dom)

	@classmethod
	def from_nouns(cls, nouns):
		return cls.from_nouns_dom(noun, cls.DOM)

	@classmethod
	def from_noun(cls, noun):
		return cls.from_nouns_dom([noun], cls.DOM)

	def wikicode(self, key):
		return self.json["query"]["pages"][key]["revisions"][0]["*"]

	def revision_time(self, key):
		return self.json["query"]["pages"][key]["revisions"][0]["timestamp"]

	def _get_translations(self, reg):
		res = re.findall(reg, self.wikicode(), re.M)
		return [r.decode("utf-8") for r in res]

class FrenchNounPage(NounPage):
	DOM = "fr"

	def get_english(self):
		return self._get_translations("\{\{trad[+-]\|en\|(.+?)\}\}")

	def get_german(self):
		return self._get_translations("\{\{trad[+-]\|de\|(.+?)\}\}")

	def get_latvian(self):
		return self._get_translations("\{\{trad[+-]\|lv\|(.+?)\}\}")

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
