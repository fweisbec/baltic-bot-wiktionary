#!/usr/bin/python
# -*- coding: utf8 -*-

import requests
import WikiLogin

class WiktionaryCookie(dict):
	_instance = None

	@staticmethod
	def getInstance():
		if not WiktionaryCookie._instance:
			WiktionaryCookie._instance = WiktionaryCookie()
		return WiktionaryCookie._instance

	def __init__(self):
		data = {"action" : "login", "lgname" : WikiLogin.USER, "lgpassword" : WikiLogin.PASS, "format" : "json"}
		r = requests.post("http://fr.wiktionary.org/w/api.php", data = data)
		cookies = r.cookies
		token = r.json()["login"]["token"]
		data["lgtoken"] = token
		r = requests.post("http://fr.wiktionary.org/w/api.php", data = data, cookies = cookies)
		self.update(r.cookies)

if __name__ == "__main__":
	print WiktionaryCookie()

# Read page: http://en.wikipedia.org/w/api.php?format=json&action=query&titles=Albert%20Einstein&prop=revisions&rvprop=content

# https://www.mediawiki.org/wiki/API:Categorymembers
# List from category: https://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:English%20nouns
