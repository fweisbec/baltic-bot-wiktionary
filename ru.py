#!/usr/bin/python
# -*- coding: utf8 -*-

import os, sys, optparse
from termcolor import colored

import WiktionaryCookie
from Wikicode import *
from Page import *
from Iterator import *

"""
===Pronunciation===
* {{ru-IPA|де́лать}}
* {{audio|Ru-делать.ogg|lang=ru|Audio}}

===Verb===
{{ru-verb|де́лать|impf|pf=сде́лать}}
"""

class RuWikicode(object):
	def __init__(self, wikicode):
		self.wikicode = wikicode
		self.parsed = mwparserfromhell.parse(wikicode)
		self.parsed = self.parsed.get_sections(matches = "{{-ru-}}")[0]

	def pron(self):
		section = self.parsed.get_sections(matches = u"Произношение")[0]
		for i in section.ifilter_templates():
			if i.name.encode("utf8") == "transcription":
				return i.params[0]
		return None


def pron(word):
	# Get russian page
	wru = RussianNounPage.from_noun(word)
	if wru.error():
		return None
	key = wru.key(word)
	wikicode = wru.wikicode(key)

	wru = RuWikicode(wikicode)
	return wru.pron()

def main():
	title = u"делать"
	p = RussianNounPage.from_noun(title)
	key = p.key(title)
	wikicode = p.wikicode(key)
	r = RuWikicode(wikicode)
	print r.pron()

if __name__ == "__main__":
	main()
