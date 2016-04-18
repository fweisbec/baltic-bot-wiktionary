#!/usr/bin/python
# -*- coding: utf8 -*-

class Gender:
	NAME = None

class MaleGender(Gender):
	NAME = u"Masculin"

class FemaleGender(Gender):
	NAME = u"Feminin"

class NeutralGender(Gender):
	NAME = u"Neutral"


class Number:
	NAME = None
	CODE = None

class SingularNumber(Number):
	NAME = u"Singular"
	CODE = u"s"

class PluralNumber(Number):
	NAME = u"Plural"
	CODE = u"p"


class Case:
	NAME = None
	CODE = None

class NominatifCase(Case):
	NAME = u"Nominatif"
	CODE = u"n"

class GenitifCase(Case):
	NAME = u"Génitif"
	CODE = u"g"

class DatifCase(Case):
	NAME = u"Datif"
	CODE = u"d"

class AccusatifCase(Case):
	NAME = u"Accusatif"
	CODE = u"a"

class InstrumentalCase(Case):
	NAME = u"Instrumental"
	CODE = u"i"

class PrepositionnelCase(Case):
	NAME = u"Prépositionnel"
	CODE = u"l"

class VocatifCase(Case):
	NAME = u"Vocatif"
	CODE = u"v"

class PartitifCase(Case):
	NAME = u"Partitif"
	CODE = u"p"

class Flexion:
	def __init__(self, val, case):
		self.val = val
		self.case = case

	def set(self, val):
		self.val = val

	def __eq__(self, other):
		if self.val != other.val:
			return False
		if self.case != other.case:
			return False
		return True

class NounFlexion(Flexion):
	def __init__(self, val, case, number):
		Flexion.__init__(self, val, case)
		self.number = number

	def __eq__(self, other):
		if not Flexion.__eq__(self, other):
			return False

		if self.number != other.number:
			return False
		return True

class NounFlexions:
	def __init__(self, *args):
		self.flexions = []
		for arg in args:
			self.flexions.append(arg)

	def add_flexion(self, val, case, number):
		flexion = NounFlexion(val, case, number)
		self.flexions.append(flexion)

	@staticmethod
	def strip_accent(word):
		return word.replace(u'\u0301', "")

	def format_acronyms(self):
		acronyms = {}
		for flexion in self.flexions:
			word_acc = flexion.val
			word = self.strip_accent(word_acc)
			arg = u"%sx%s" % (flexion.case.CODE, flexion.number.CODE)
			if word not in acronyms:
				acronyms[word] = {word_acc : [arg]}
			elif word_acc not in acronyms[word]:
				acronyms[word][word_acc] = [arg]
			else:
				acronyms[word][word_acc].append(arg)

		return acronyms

	def __repr__(self):
		return self.flexions.__repr__()

	def __eq__(self, other):
		if len(self.flexions) != len(other.flexions):
			return False

		for flexion in self.flexions:
			match = False
			for other_flexion in other.flexions:
				if flexion == other_flexion:
					match = True
					break
			if not match:
				return False

		return True



class RuNounFlexions(NounFlexions):
	pass
