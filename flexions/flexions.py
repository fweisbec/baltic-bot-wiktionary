#!/usr/bin/python
# -*- coding: utf8 -*-

class Gender:
	def __init__(self, name, code):
		self.name = name
		self.code = code

MaleGender = Gender(u"Masculin", u"m")
NeutralGender = Gender(u"Neutral", u"n")
FemaleGender = Gender(u"Feminin", u"f")


class Number:
	def __init__(self, name, code):
		self.name = name
		self.code = code

	def __repr__(self):
		return self.name

SingularNumber = Number(u"Singular", u"s")
PluralNumber = Number(u"Plural", u"p")


class Case:
	def __init__(self, name, code):
		self.name = name
		self.code = code

	def __repr__(self):
		return self.name

NominatifCase = Case(u"Nominatif", u"n")
GenitifCase = Case(u"Génitif", u"g")
DatifCase = Case(u"Datif", u"d")
AccusatifCase = Case(u"Accusatif", u"a")
InstrumentalCase = Case(u"Instrumental", u"i")
PrepositionnelCase = Case(u"Prépositionnel", u"l")
VocatifCase = Case(u"Vocatif", u"v")
PartitifCase = Case(u"Partitif", u"p")

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

	def __repr__(self):
		return u"%s %s" % (self.case, self.val)

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

	def __repr__(self):
		return u"%s %s" % (Flexion.__repr__(self), self.number)

class AdjectiveFlexion(Flexion):
	def __init__(self, val, case, number, gender, animate = None):
		Flexion.__init__(self, val, case)
		self.number = number
		self.gender = gender
		self.animate = animate

	def __eq__(self, other):
		if not Flexion.__eq__(self, other):
			return False

		if self.number != other.number or self.gender != other.gender:
			return False
		return True

	def __repr__(self):
		return u"%s %s %s %s" % (Flexion.__repr__(self), self.number, self.gender, self.animate)

class RuFlexions:
	def __init__(self):
		self.flexions = []

	@staticmethod
	def strip_accent(word):
		return word.replace(u'\u0301', "")

	@classmethod
	def add_acronym(cls, acronyms, word_acc, arg):
		word = cls.strip_accent(word_acc)
		if word not in acronyms:
			acronyms[word] = {word_acc : [arg]}
		elif word_acc not in acronyms[word]:
			acronyms[word][word_acc] = [arg]
		else:
			acronyms[word][word_acc].append(arg)

	def __repr__(self):
		ret = u"Flexions: %d" % len(self.flexions)
		for flexion in self.flexions:
			ret += u"\n"
			ret += flexion.__repr__()
		return ret.encode("utf8")

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

class RuNounFlexions(RuFlexions):
	def __init__(self, *args):
		RuFlexions.__init__(self)
		for arg in args:
			self.flexions.append(arg)

	def add_flexion(self, val, case, number):
		flexion = NounFlexion(val, case, number)
		self.flexions.append(flexion)

	def format_acronyms(self):
		acronyms = {}
		for flexion in self.flexions:
			arg = u"%sx%s" % (flexion.case.code, flexion.number.code)
			self.add_acronym(acronyms, flexion.val, arg)

		return acronyms

class RuAdjectiveFlexions(RuFlexions):
	def __init__(self):
		self.flexions = []

	def add_flexion(self, val, case, number, gender, animate):
		flexion = AdjectiveFlexion(val, case, number, gender, animate)
		self.flexions.append(flexion)

	@staticmethod
	def strip_accent(word):
		return word.replace(u'\u0301', "")

	def format_acronyms(self):
		acronyms = {}
		for flexion in self.flexions:			
			arg = u"%s" % flexion.case.code
			if flexion.number is SingularNumber:
				arg += u"%sx" % flexion.gender.code
			elif flexion.number is PluralNumber:
				arg += u"x%s" % flexion.number.code
			else:
				raise NotImplementedError

			if flexion.animate is True:
				arg += u"a"
			elif flexion.animate is False:
				arg += u"i"

			self.add_acronym(acronyms, flexion.val, arg)

		return acronyms
