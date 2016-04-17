#!/usr/bin/python
# -*- coding: utf8 -*-

import requests, re

class HtmlFrRu:
	cases = { \
		 u"Nominatif"       : "n", \
		 u"Génitif"         : "g", \
		 u"Datif"           : "d", \
		 u"Accusatif"       : "a", \
		 u"Instrumental"    : "i", \
		 u"Prépositionnel"  : "l", \
		 u"Vocatif"         : "v", \
		 u"Partitif"        : "p"  \
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

	@classmethod
	def prepare_flexion(cls, is_plur, couple, case, flexions):
		if is_plur:
			idx = 1
			c = "p"
		else:
			idx = 0
			c = "s"
			
		for flexion_acc in couple[idx]:
			flexion = flexion_acc.replace(u'\u0301', "")
			arg = "%sx%s" % (cls.cases[case], c)
			if flexion not in flexions:
				flexions[flexion] = {flexion_acc : [arg]}
			elif flexion_acc not in flexions[flexion]:
				flexions[flexion][flexion_acc] = [arg]
			else:
				flexions[flexion][flexion_acc].append(arg)

	def flexions_args(self):
		flexions = { }

		for case in self.cases:
			couple = self.case(case)
			if couple is None and case in ("Vocatif", "Partitif"):
				continue
			self.prepare_flexion(0, couple, case, flexions)
			self.prepare_flexion(1, couple, case, flexions)

		for flexion in flexions:
			yield (flexion, flexions[flexion])
			
