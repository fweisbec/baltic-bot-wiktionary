#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, re
from flexions.flexions import *

class HtmlFrRu:
	def __init__(self, word):
		self.word = word
		r = requests.get(u"http://fr.wiktionary.org/wiki/%s" % word)
		self.html = r.text

	def flexions_args(self):
		flexions = self.flexions()

		acronyms = flexions.format_acronyms()
		for acronym in acronyms:
			yield (acronym, acronyms[acronym])

class HtmlFrRuAdj(HtmlFrRu):
	def nominatif(self):
		s = re.search(u"""<th[^>]+>Nominatif</th>\s+<td><strong class="selflink">([^<]+)</strong></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>""", self.html, re.U | re.S)
		if s is None:
			return None
		else:
			return (s.group(1), s.group(2), s.group(3), s.group(4))

	def __simple_case(self, name):
		s = re.search(u"""<th colspan="2">%s</th>\s+<td colspan="2"><a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+</tr>""" % name, self.html, re.U | re.S)
		if s is not None:
			return (s.group(1), s.group(1), s.group(2), s.group(3))

		s = re.search(u"""<th colspan="2">%s</th>\s+<td colspan="2"><a href=[^>]+>([^<]+)</a></td>\s+<td><strong class="selflink">([^<]+)</strong></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+</tr>""" % name, self.html, re.U | re.S)
		if s is not None:
			return (s.group(1), s.group(1), s.group(2), s.group(3))

		return None

	def genitif(self):
		return self.__simple_case(u"Génitif")

	def datif(self):
		return self.__simple_case(u"Datif")

	def prepositionnel(self):
		return self.__simple_case(u"Prépositionnel")

	def instrumental(self):
		s = re.search(u"""<th colspan="2">Instrumental</th>\s+<td colspan="2"><a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a>\s+/\s+<a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+</tr>""", self.html, re.U | re.S)
		if s is not None:
			return (s.group(1), s.group(1), s.group(2), s.group(3), s.group(4))

		s = re.search(u"""<th colspan="2">Instrumental</th>\s+<td colspan="2"><a href=[^>]+>([^<]+)</a></td>\s+<td><strong class="selflink">([^<]+)</strong>\s+/\s+<a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+</tr>""", self.html, re.U | re.S)
		if s is not None:
			return (s.group(1), s.group(1), s.group(2), s.group(3), s.group(4))

		return None

	def accusatif(self):
		s = re.search(u"""<tr>\s+<th[^>]+>Accusatif</th>\s+<th>Animé</th>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+<td rowspan="2"><a href=[^>]+>([^<]+)</a></td>\s+<td[^>]+><a href=[^>]+>([^<]+)</a></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+</tr>\s+<tr>\s+<th>Inanimé</th>\s+<td><strong class="selflink">([^<]+)</strong></td>\s+<td><a href=[^>]+>([^<]+)</a></td>\s+</tr>""", self.html, re.U | re.S)
		if s is None:
			return None
		else:
			return (s.group(1), s.group(2), s.group(3), s.group(4), s.group(5), s.group(6))

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

class HtmlFrRuNoun(HtmlFrRu):
	cases = { \
		 u"Nominatif"       : ("n", NominatifCase),		\
		 u"Génitif"         : ("g", GenitifCase),		\
		 u"Datif"           : ("d", DatifCase),			\
		 u"Accusatif"       : ("a", AccusatifCase),		\
		 u"Instrumental"    : ("i", InstrumentalCase),	\
		 u"Prépositionnel"  : ("l", PrepositionnelCase),\
	}

	def nominatif(self):
		s = re.search(u"<tr>\s*<th>Nominatif</th>\s*<td><strong class=\"selflink\">(\w|\u0301|\ucc81)+?</strong></td>[^<]*?<td><a href=\"/w/index.php[?]title=[^\"]+?\" class=\"new\" title=\"[^\"]+?\">((\w|\u0301|\ucc81)+?)</a></td>", self.html, re.U | re.S)
		return s.group(2)


	def case(self, name):
		# Nominatif
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td>\s*<span[^>]+><a class=[^>]+?>([^<]+?)</a></span></td>\s*<td><span[^>]+><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1)], [s.group(2)])

		# Cas normal: deux rouges
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td>\s*<span[^>]+><a href=[^>]+?>([^<]+?)</a></span></td>\s*<td><span[^>]+><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1)], [s.group(2)])

		#s = re.search(u"<tr>\s*<th>%s</th>\s*<td>\s*<span[^>]+><a href=[^>]+?>([^<]+?)</a></span><br />[^<]*?<a href=[^>]+?>([^<]+?)</a></td>\s*<td><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		#if s:
		#	return ([s.group(1), s.group(2)], [s.group(3)])
		
		# Instrumental féminin
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td>\s*<span[^>]+><a href=[^>]+?>([^<]+?)</a></span><br />[^<]*?<span[^>]+><a href=[^>]+?>([^<]+?)</a></span></td>\s*<td><span[^>]+><a href=[^>]+?>([^<]+?)</a></span>" % name, self.html, re.U | re.S)
		if s:
			return ([s.group(1), s.group(2)], [s.group(3)])
			
		#s = re.search(u"<tr>\s*<th>%s</th>\s*<td><span[^>]+><strong class=\"selflink\">([^<]+?)</strong></span></td>[^<]*?<td><span[^>]+><a href=[^>]+?>([^<]+?)</a>" % name, self.html, re.U | re.S)
		#if s:
		#	return ([s.group(1)], [s.group(2)])
		
		# Euh...
		s = re.search(u"<tr>\s*<th>%s</th>\s*<td><span[^>]+><a href=[^>]+?>([^<]+?)</a></span></td>\s*<td><span[^>]+><strong class=\"selflink\">([^<]+?)</strong>" % name, self.html, re.U | re.S)
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

	def has_red_link(self):
		s = re.search(u"""<td><a href="/w/index.php\?title=[^;]+?;action=edit&amp;redlink=1" class="new" title="\w+? \(page inexistante\)">[^<]+?</a></td>""", self.html, re.S | re.U | re.M)
		return s is not None
