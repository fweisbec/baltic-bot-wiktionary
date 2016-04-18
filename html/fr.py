#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, re
from flexions.flexions import *

class HtmlFrRu:
	cases = { \
		 u"Nominatif"       : ("n", NominatifCase),		\
		 u"Génitif"         : ("g", GenitifCase),		\
		 u"Datif"           : ("d", DatifCase),			\
		 u"Accusatif"       : ("a", AccusatifCase),		\
		 u"Instrumental"    : ("i", InstrumentalCase),	\
		 u"Prépositionnel"  : ("l", PrepositionnelCase),\
		 u"Vocatif"         : ("v", VocatifCase),		\
		 u"Partitif"        : ("p", PartitifCase)		\
	}
		
	def __init__(self, word):
		self.word = word
		r = requests.get(u"http://fr.wiktionary.org/wiki/%s" % word)
		self.html = r.text
		#print self.html.encode("utf8")

	def nominatif(self):
		s = re.search(u"<tr>\s*<th>Nominatif</th>\s*<td><strong class=\"selflink\">(\w|\u0301|\ucc81)+?</strong></td>[^<]*?<td><a href=\"/w/index.php[?]title=[^\"]+?\" class=\"new\" title=\"[^\"]+?\">((\w|\u0301|\ucc81)+?)</a></td>", self.html, re.U | re.S)
		return s.group(2)

	def case(self, name):
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td>\s*<a href=[^>]+?>([^<]+?)</a></td>\s*<td><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1)], [s.group(2)])
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td>\s*<a href=[^>]+?>([^<]+?)</a><br />[^<]*?<a href=[^>]+?>([^<]+?)</a></td>\s*<td><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1), s.group(2)], [s.group(3)])
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td><strong class=\"selflink\">([^<]+?)</strong></td>[^<]*?<td><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1)], [s.group(2)])
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td><a href=[^>]+?>([^<]+?)</a></td>\s*<td><strong class=\"selflink\">([^<]+?)</strong></td>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1)], [s.group(2)])
		return None

	def flexions(self):
		ret = RuNounFlexions()

		for case in self.cases:
			couple = self.case(case)
			if couple is None and case in ("Vocatif", "Partitif"):
				continue

			for flexion in couple[0]:
				ret.add_flexion(flexion, self.cases[case][1], SingularNumber)
			for flexion in couple[1]:
				ret.add_flexion(flexion, self.cases[case][1], PluralNumber)
		return ret

	def flexions_args(self):
		flexions = self.flexions()

		acronyms = flexions.format_acronyms()
		for acronym in acronyms:
			yield (acronym, acronyms[acronym])	
