#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, re, sys
from flexions.flexions import *

class HtmlRuRu:
	cases = { \
		 u"именительный"	: ("n", NominatifCase),		\
		 u"родительный"		: ("g", GenitifCase),		\
		 u"дательный"		: ("d", DatifCase),			\
		 u"винительный"		: ("a", AccusatifCase),		\
		 u"творительный"	: ("i", InstrumentalCase),	\
		 u"предложный"		: ("l", PrepositionnelCase) \
	}
		
	def __init__(self, word):
		self.word = word
		r = requests.get(u"http://ru.wiktionary.org/wiki/%s" % word)
		self.html = r.text
		#print self.html.encode("utf8")

	def case(self, name):
		s = re.search(u"""<a href="/wiki/[^"]+" title="%s">[^<]+?</a></td>\s*<td bgcolor="#FFFFFF">([^<]+?)</td>\s*<td bgcolor="#FFFFFF">([^<]+?)</td>\s*</tr>""" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1)], [s.group(2)])
		s = re.search(u"""<a href="/wiki/[^"]+" title="%s">.+?</a></td>\s*<td bgcolor="#FFFFFF">([^<]+?)<br\s*/>\s*([^<]+?)</td>\s*<td bgcolor="#FFFFFF">([^<]+?)</td>\s*</tr>""" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1), s.group(2)], [s.group(3)])
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

