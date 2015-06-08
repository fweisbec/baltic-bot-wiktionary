#!/usr/bin/python
# -*- coding: utf8 -*-

import sys

lv_default_phonology = {
	u"a" : u"a",
	u"ā" : u"a:",
	u"b" : u"b",
	u"c" : u"t͡s",
	u"č" : u"t͡ʃ",
	u"d" : u"d",
	u"dz": u"d͡z",
	u"dž": u"d͡ʒ",
	u"e" : u"ɛ",
	u"ē" : u"ɛ:",
	u"f" : u"f",
	u"g" : u"g",
	u"ģ" : u"ɟ",
	u"h" : u"x",
	u"i" : u"i",
	u"ī" : u"i",
	u"j" : u"j",
	u"k" : u"k",
	u"ķ" : u"c",
	u"l" : u"l",
	u"ļ" : u"ʎ",
	u"m" : u"m",
	u"n" : u"n",
	u"ņ" : u"ɲ",
	u"o" : u"uo",
	u"p" : u"p",
	u"r" : u"r",
	u"ŗ" : u"r",
	u"s" : u"s",
	u"š" : u"ʃ",
	u"t" : u"t",
	u"u" : u"u",
	u"ū" : u"u:",
	u"v" : u"v",
	u"z" : u"z",
	u"ž" : u"ʒ"
}

def main():
	guess = ""
	w = sys.argv[1].decode("utf-8")
	start = 0
	while start < len(w):
		l = w[start:start+2]
		if l in lv_default_phonology:
			guess += lv_default_phonology[l]
			start += 2
		elif l[0] in lv_default_phonology:
			guess += lv_default_phonology[l[0]]
			start += 1
		else:
			print "%s not in range(%d:%d)" % (l, start, start + 2)
	print guess

if __name__ == "__main__":
	main()
