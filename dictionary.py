# generate a dictionary
import gensim
import nltk
import pdb

f = "/Users/Welleck/own_files/datasets/stack_exchange/sep1m.txt"
outfile = "stack_exchange_dictionary.txt"
toks = nltk.tokenize.punkt.PunktWordTokenizer().tokenize(open(f).read())
dictionary = gensim.corpora.dictionary.Dictionary([toks])
bag_of_words = dictionary.doc2bow(toks)
good_ids = map(lambda y: y[0], filter(lambda x: x[1] > 20, bag_of_words))
dictionary.filter_tokens(bad_ids=None, good_ids=good_ids)
with open(outfile, 'w') as of:
	for word in dictionary.values():
		of.write("{0}\n".format(word.lower()))
