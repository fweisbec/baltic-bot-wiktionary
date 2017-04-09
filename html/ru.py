#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, re, sys
from flexions.flexions import *

class HtmlRuRu:
	def __init__(self, word):
		self.word = word
		r = requests.get(u"http://ru.wiktionary.org/wiki/%s" % word)
		self.html = r.text
		# Hack to avoid case collision from serbian table in the same page
		self.html = self.html.split(u"""<span class="mw-headline" id=".D0.A1.D0.B5.D1.80.D0.B1.D1.81.D0.BA.D0.B8.D0.B9">Сербский</span>""")[0]

	def flexions_args(self):
		flexions = self.flexions()

		acronyms = flexions.format_acronyms()
		for acronym in acronyms:
			yield (acronym, acronyms[acronym])

class HtmlRuRuAdj(HtmlRuRu):
	def __simple_case(self, name):
		s = re.search(u"""<tr>\s+<td[^>]+><a href=[^>]+>%s</a></td>\s+<td>([^<]+)</td>\s+<td>([^<]+)</td>\s+<td>([^<]+)</td>\s+<td>([^<]+)</td>\s+</tr>""" % name, self.html, re.S | re.U)
		if s is not None:
			return (s.group(1), s.group(2), s.group(3), s.group(4))
		else:
			return None
		
	def nominatif(self):
		return self.__simple_case(u"Им.")

	def genitif(self):
		return self.__simple_case(u"Рд.")

	def datif(self):
		return self.__simple_case(u"Дт.")

	def prepositionnel(self):
		return self.__simple_case(u"Пр.")

	def instrumental(self):
		(m, n, f, p) = self.__simple_case(u"Тв.")
		(f1, f2) = f.split(" ")
		return (m, n, f1, f2, p)

	def accusatif(self):
		s = re.search(u"""<tr>\s+<td[^>]+><a href=[^>]+>Вн.</a>[^<]+</td>\s+<td[^>]+>одуш.</td>\s+<td>([^<]+)</td>\s+<td rowspan="2">([^<]+)</td>\s+<td rowspan="2">([^<]+)</td>\s+<td>([^<]+)</td>\s+</tr>\s+<tr>\s+<td[^>]+>неод.</td>\s+<td>([^<]+)</td>\s+<td>([^<]+)</td>\s+</tr>""", self.html, re.S | re.U)
		if s is not None:
			return (s.group(1), s.group(2), s.group(3), s.group(4), s.group(5), s.group(6))
		else:
			return None

	def flexions(self):
		ret = RuAdjectiveFlexions()

		(m, n, f, p) = self.nominatif()
		ret.add_flexion(m, NominatifCase, SingularNumber, MaleGender, None)
		ret.add_flexion(n, NominatifCase, SingularNumber, NeutralGender, None)
		ret.add_flexion(f, NominatifCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(p, NominatifCase, PluralNumber, None, None)

		(m, n, f, p) = self.genitif()
		ret.add_flexion(m, GenitifCase, SingularNumber, MaleGender, None)
		ret.add_flexion(n, GenitifCase, SingularNumber, NeutralGender, None)
		ret.add_flexion(f, GenitifCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(p, GenitifCase, PluralNumber, None, None)

		(m, n, f, p) = self.datif()
		ret.add_flexion(m, DatifCase, SingularNumber, MaleGender, None)
		ret.add_flexion(n, DatifCase, SingularNumber, NeutralGender, None)
		ret.add_flexion(f, DatifCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(p, DatifCase, PluralNumber, None, None)

		(m, n, f, p) = self.prepositionnel()
		ret.add_flexion(m, PrepositionnelCase, SingularNumber, MaleGender, None)
		ret.add_flexion(n, PrepositionnelCase, SingularNumber, NeutralGender, None)
		ret.add_flexion(f, PrepositionnelCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(p, PrepositionnelCase, PluralNumber, None, None)

		(m, n, f, f2, p) = self.instrumental()
		ret.add_flexion(m, InstrumentalCase, SingularNumber, MaleGender, None)
		ret.add_flexion(n, InstrumentalCase, SingularNumber, NeutralGender, None)
		ret.add_flexion(f, InstrumentalCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(f2, InstrumentalCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(p, InstrumentalCase, PluralNumber, None, None)

		(ma, n, f, pa, m, p) = self.accusatif()
		ret.add_flexion(ma, AccusatifCase, SingularNumber, MaleGender, True)
		ret.add_flexion(m, AccusatifCase, SingularNumber, MaleGender, False)
		ret.add_flexion(n, AccusatifCase, SingularNumber, NeutralGender, None)
		ret.add_flexion(f, AccusatifCase, SingularNumber, FemaleGender, None)
		ret.add_flexion(pa, AccusatifCase, PluralNumber, None, True)
		ret.add_flexion(p, AccusatifCase, PluralNumber, None, False)

		return ret

class HtmlRuRuNoun(HtmlRuRu):
	cases = { \
		 u"именительный"	: ("n", NominatifCase),		\
		 u"родительный"		: ("g", GenitifCase),		\
		 u"дательный"		: ("d", DatifCase),			\
		 u"винительный"		: ("a", AccusatifCase),		\
		 u"творительный"	: ("i", InstrumentalCase),	\
		 u"предложный"		: ("l", PrepositionnelCase) \
	}

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

