# Generate a dictionary / vocabulary from a text dataset.

import gensim
import nltk
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("dataset", type=str, help="Input dataset filename.")
argparser.add_argument("-o", "--outfile", dest="outfile", default='vocab.txt', help="Output filename. (default='vocab.txt')")
args = argparser.parse_args()

def generate(f, outfile):
	toks = nltk.tokenize.punkt.PunktWordTokenizer().tokenize(open(f).read())
	dictionary = gensim.corpora.dictionary.Dictionary([toks])
	bag_of_words = dictionary.doc2bow(toks)
	good_ids = map(lambda y: y[0], filter(lambda x: x[1] > 20, bag_of_words))
	dictionary.filter_tokens(bad_ids=None, good_ids=good_ids)
	with open(outfile, 'w') as of:
		for word in dictionary.values():
			of.write("{0}\n".format(word.lower()))

generate(args.dataset, args.outfile)