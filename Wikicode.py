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
		txt = re.sub(u"\[\[[a-z-]+:%s\]\]\n?" % word, "", txt, count = 500, flags = re.M | re.U)
		txt = txt.rstrip() + "\n\n"
		for dom in doms:
			txt += u"[[%s:%s]]\n" % (dom, word)
		return txt

	def suppr_doms(self, word, doms):
		txt = self.wikicode
		for dom in doms:
			txt = re.sub(u"\[\[%s:%s\]\]\n?" % (dom, word), "", txt, count = 500, flags = re.M | re.U)
		return txt.rstrip()

	def add_category(self, cat):
		parsed = mwparserfromhell.parse(self.wikicode)
		section = parsed.get_sections(matches = lambda x: u"langue" in x and u"es" in x)
		if not section:
			return parsed

		section = section[0]
		i = 0

		line = True
		while True:
			i -= 1
			prev = section.get(i)
			if prev.startswith(u"[[Catégorie"):
				line = False
				break
			if re.match("\s+", prev.encode("utf8").decode("utf8"), re.U | re.M):
				continue
			if re.match("\[\[[a-z-]+:(.+?)\]\]\s*", prev.encode("utf8").decode("utf8"), re.S | re.U | re.M):
				continue
			break

		insert = "\n" + cat + "\n\n"
		if line:
			insert = "\n" + insert
		section.insert_after(prev, insert)
			
		return parsed

class Editor(object):
	def __init__(self, noun, wikicode, basetimestamp):
		self.noun = noun
		self.basetimestamp = basetimestamp
		self.old = wikicode
		self.new = wikicode

	def add_translation_de(self, de, info):
		w = WikicodeFrench(self.new)
		self.new = w.add_translation_de(de, info)

	def add_decl_1st(self):
		w = WikicodeFrench(self.new)
		self.new = w.add_decl_1st(self.noun)

	def update_doms(self, doms):
		w = WikicodeFrench(self.new)
		self.new = w.update_doms(self.noun, doms)

	def suppr_doms(self, doms):
		w = WikicodeFrench(self.new)
		self.new = w.suppr_doms(self.noun, doms)

	def replace(self, old, new):
		prev = self.new
		self.new = self.new.replace(old, new)
		if prev == self.new:
			return False
		else:
			return True

	def reg_replace(self, old, new, ignore_case):
		flags = re.U | re.M | re.S
		if ignore_case:
			flags |= re.I
		prev = self.new
		self.new = re.sub(old, new, self.new, flags = flags)
		if prev == self.new:
			return False
		else:
			return True

	def diff(self):
		ret = ""
		old = self.old.splitlines()
		new = self.new.splitlines()
		for line in difflib.unified_diff(old, new):
			ret += line + "\n"
		return ret

	def add_category(self, cat):
		txt = self.new
		cat = u"[[Catégorie:%s]]" % cat
		if cat in txt:
			return False
		w = WikicodeFrench(self.new)
		self.new = w.add_category(cat)

		return True

	def commit(self, summary, minor = False):
		tkpage = JsonPage("https://fr.wiktionary.org/w/api.php?action=query&meta=tokens&format=json")
		token = tkpage.json["query"]["tokens"]["csrftoken"]
		post = {
			"action" : "edit",
			"title"  : self.noun.encode("utf-8"),
			"summary": summary,
			"text"   : self.new.encode("utf-8"),
			"basetimestamp" : self.basetimestamp,
			"token" : token,
			"bot"	: ""
		}

		if minor:
			post["minor"] = ""

		url = "https://fr.wiktionary.org/w/api.php"
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		req = requests.post(url, data = post, cookies = cookies)
		cookies.update(req.cookies)

class Creator(object):
	def __init__(self, word, wikicode):
		self.word = word
		self.wikicode = wikicode

	def commit(self, bot = False):
		tkpage = JsonPage("https://fr.wiktionary.org/w/api.php?action=query&meta=tokens&format=json")
		token = tkpage.json["query"]["tokens"]["csrftoken"]
		post = {
			"action" : "edit",
			"title"  : self.word.encode("utf-8"),
			"text"   : self.wikicode.encode("utf-8"),
			"createonly" : "1",
			"token" : token,
		}

		if bot:
			post["bot"] = ""

		url = "https://fr.wiktionary.org/w/api.php"
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		req = requests.post(url, data = post, cookies = cookies)
		cookies.update(req.cookies)

class Renamer(object):
	def __init__(self, old, new):
		self.old = old
		self.new = new

	def commit(self, summary):
		tkpage = JsonPage("https://fr.wiktionary.org/w/api.php?action=query&meta=tokens&format=json")
		token = tkpage.json["query"]["tokens"]["csrftoken"]
		post = {
			"action"		: "move",
			"from"			: self.old.encode("utf-8"),
			"to"			: self.new.encode("utf-8"),
			"movetalk"		: "",
			"movesubpages"	: "",
			"reason"		: summary,
			"token"			: token,
		}
		url = "https://fr.wiktionary.org/w/api.php"
		cookies = WiktionaryCookie.WiktionaryCookie.getInstance()
		req = requests.post(url, data = post, cookies = cookies)
		cookies.update(req.cookies)


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
