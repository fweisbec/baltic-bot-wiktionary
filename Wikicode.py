#!/usr/bin/python
# -*- coding: utf8 -*-

import re, mwparserfromhell, sys, difflib, requests
from Page import *

class WikicodeFrench(object):
	def __init__(self, wikicode):
		self.wikicode = wikicode

	def add_translation_de(self, de, info):
		parsed = mwparserfromhell.parse(self.wikicode)
		translations = parsed.get_sections(matches = "traductions")
		if len(translations) != 1:
			print "More than one translation section"
			raise NotImplementedError

		translation = translations[0]
		tpl = translation.filter_templates()
		prev = None
		for t in tpl:
			name = t.name.encode("utf-8")
			if name == "trad-début":
				if prev is not None:
					print "More than one translation subsection"
					raise NotImplementedError
				prev = t
				continue
			m = re.match("^trad[-+][-]?$", name)
			if m is None:
				continue
			lang = t.params[0]
			if lang in ("aa", "sq", "ale"):
				if prev is not None:
					prev = t
			elif lang == "de":
				print "Pre-existing .de"
				raise NotImplementedError

		if prev is None:
			print "Empty translation"
			raise NotImplementedError
		txt = "\n* {{T|de}} : {{trad+|de|%s}}" % de
		if info:
			txt += " %s" % info
		new_tpl = mwparserfromhell.nodes.text.Text(txt)
		parsed.insert_after(prev, new_tpl)
		return parsed.encode("utf-8")

	def add_decl_1st(self, word):
		parsed = mwparserfromhell.parse(self.wikicode)
		prev = u"=== {{S|nom|lv}} ===\n"
		txt = u"{{lv-décl-m-s|%s}}\n" % word[:-1]
		decl = mwparserfromhell.nodes.text.Text(txt)
		parsed.insert_after(prev, decl)
		return parsed.encode("utf-8")

	def update_doms(self, word, doms):
		txt = self.wikicode
		txt = re.sub(u"\[\[[a-z-]+:%s\]\]\n?" % word, "", txt, re.M | re.U)
		# Not sure why but I need to do it twice in order to remove all of them
		txt = re.sub(u"\[\[[a-z-]+:%s\]\]\n?" % word, "", txt, re.M | re.U)
		txt = txt.rstrip() + "\n\n"
		for dom in doms:
			txt += u"[[%s:%s]]\n" % (dom, word)
		return txt
		

class Editor(object):
	def __init__(self, noun):
		# First get base rev time
		rev = RevisionFrenchPage.from_noun(noun)
		self.basetimestamp = rev.revision_time()
		# Get noun page
		self.noun = FrenchNounPage.from_noun(noun)
		self.old = self.noun.wikicode()
		self.new = self.noun.wikicode()

	def add_translation_de(self, de, info):
		w = WikicodeFrench(self.new)
		self.new = w.add_translation_de(de, info)

	def add_decl_1st(self):
		w = WikicodeFrench(self.new)
		self.new = w.add_decl_1st(self.noun.noun)

	def update_doms(self, doms):
		w = WikicodeFrench(self.new)
		self.new = w.update_doms(self.noun.noun, doms)

	def diff(self):
		ret = ""
		old = self.old.splitlines()
		new = self.new.splitlines()
		for line in difflib.unified_diff(old, new):
			ret += line + "\n"
		return ret

	def commit(self, summary):
		tkpage = JsonPage("http://fr.wiktionary.org/w/api.php?action=query&meta=tokens&format=json")
		token = tkpage.json["query"]["tokens"]["csrftoken"]
		post = {
			"action" : "edit",
			"title"  : self.noun.noun.encode("utf-8"),
			"summary": summary,
			"text"   : self.new.encode("utf-8"),
			"basetimestamp" : self.basetimestamp,
			"token" : token
		}
		url = "http://fr.wiktionary.org/w/api.php"
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		self.req = requests.post(url, data = post, cookies = cookies)
		cookies.update(self.req.cookies)

class Creator(object):
	def __init__(self, word, wikicode):
		self.word = word
		self.wikicode = wikicode

	def commit(self, summary):
		tkpage = JsonPage("http://fr.wiktionary.org/w/api.php?action=query&meta=tokens&format=json")
		token = tkpage.json["query"]["tokens"]["csrftoken"]
		post = {
			"action" : "edit",
			"title"  : self.word.encode("utf-8"),
			"summary": summary.encode("utf-8"),
			"text"   : self.wikicode.encode("utf-8"),
			"createonly" : "1",
			"token" : token
		}
		url = "http://fr.wiktionary.org/w/api.php"
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		self.req = requests.post(url, data = post, cookies = cookies)
		cookies.update(self.req.cookies)

__code_test = """
==== {{S|synonymes}} ====
* [[froideur]]
* [[froidure]]
* [[frette]] {{Québec|nocat=1}}

==== {{S|antonymes}} ====
* [[chaleur]]

==== {{S|dérivés}} ====
* [[être en froid]] avec quelqu’un
* [[grand froid]]
* [[vague de froid]]

==== {{S|traductions}} ====
{{trad-début}}
* {{T|en}} : {{trad+|en|cold}}, {{trad+|en|coldness}}
* {{T|is}} : {{trad+|is|kuldi}}
* {{T|mg}} : {{trad--|mg|hatsiaka}}
* {{T|no}} : {{trad-|no|Kulde}}
* {{T|oc}} : {{trad+|oc|freg}}
* {{T|fa}} : {{trad+|fa|سرما}}, {{trad+|fa|برودت}}
* {{T|zdj}} : {{trad--|zdj|ɓariɗi}}, {{trad--|zdj|mazimi}}
* {{T|ses}} : {{trad--|ses|yayni}}
{{trad-fin}}

=== {{S|prononciation}} ===
* {{pron|fʁwa|fr}}
** {{pron-rég|lang=fr|France <!-- précisez svp la ville ou la région -->|fʁwa|audio=Fr-froid.ogg}}
"""

if __name__ == "__main__":
	w = WikicodeFrench(__code_test)
	trans = w.add_translation_de("prout", None)
	w.diff(trans)
