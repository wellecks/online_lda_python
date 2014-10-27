#!/usr/bin/python

#### online_lda.py | Sean Welleck, 2014
#
# Runs Hoffman's implementation ofonline Variational Bayes for LDA.
# Parses cmdline arguments to make this a more generic & reusable 
# version of Hoffman's onlinewikipedia.py.
#
# python online_lda.py --help for cmd_line options.
#
# This is a modification of code written by Matthew D. Hoffman with
# the following license:
#
# Copyright (C) 2010  Matthew D. Hoffman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cPickle, string, numpy, getopt, sys, random, time, re, pprint

import onlineldavb
import time
import sys

from printer import Printer
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("dataset", type=str, help="Input dataset filename.")
argparser.add_argument("vocab_file", help="Vocabulary filename.")
argparser.add_argument("-o", "--outdir", default='', help="Directory to place output files. (default='')")
argparser.add_argument("-b", "--batchsize", dest="batchsize", type=int, default=256, help="Batch size. (default=256)")
argparser.add_argument("-d", "--num_docs", dest="num_docs", type=int, default=7990787, help="Total # docs in dataset. (default=7990787)")
argparser.add_argument("-k", "--num_topics", dest="num_topics", type=int, default=100, help="Number of topics. (default=100)")
argparser.add_argument("-t", "--tau_0", dest="tau_0", type=int, default=1024, help="Tau learning parameter to downweight early documents (default=1024)")
argparser.add_argument("-l", "--kappa", dest="kappa", type=int, default=0.7, help="Kappa learning parameter; decay factor for influence of batches.(default=0.7)")
argparser.add_argument("-m", "--model_out_freq", dest="model_out_freq", type=int, default=10000, help="Number of iterations interval for outputting a model file. (default=10000)")

args = argparser.parse_args()

def main():

    # The number of documents to analyze each iteration.
    batchsize = args.batchsize
    # The total number of documents in the corpus.
    D = args.num_docs
    # The number of topics.
    K = args.num_topics

    # How many documents to look at
    documentstoanalyze = int(D/batchsize)

    # The vocabulary
    vocab = file(args.vocab_file).readlines()
    W = len(vocab)

    # Initialize the algorithm with alpha=1/K, eta=1/K, tau_0=1024, kappa=0.7
    alpha = 1./K  # prior on topic weights theta
    eta   = 1./K  # prior on p(w|topic) Beta
    tau_0 = args.tau_0  # learning parameter to downweight early documents
    kappa = args.kappa  # learning parameter; decay factor for influence of batches
    olda = onlineldavb.OnlineLDA(vocab, K, D, alpha, 1./K, tau_0, kappa)

    dataset_file = open(args.dataset)
    start = time.time()

    for iteration in range(0, documentstoanalyze):
        # Read a batch of articles.
        docset = batch_read(dataset_file, batchsize)
        # Give them to online LDA
        (gamma, bound) = olda.update_lambda(docset)
        # Compute an estimate of held-out perplexity
        (wordids, wordcts) = onlineldavb.parse_doc_list(docset, olda._vocab)

        # Save lambda, the parameters to the variational distributions
        # over topics, and gamma, the parameters to the variational
        # distributions over topic weights for the articles analyzed in
        # the last iteration.
        if (iteration % 10 == 0):
            i = iteration
            pct = round((i * 1.0 / documentstoanalyze) * 100, 2)
            elapsed = int(time.time() - start)
            Printer("Processed {0} batches. ~ {1}% complete. Elapsed time: {2}s"
                .format(i, pct, elapsed))
            if (iteration % args.model_out_freq == 0):
                numpy.savetxt('{0}lambda-{1}.dat'.format(args.outdir, iteration), olda._lambda)
                numpy.savetxt('{0}gamma-{1}.dat'.format(args.outdir, iteration), gamma)

    numpy.savetxt('{0}lambda-final.dat'.format(args.outdir), olda._lambda)
    numpy.savetxt('{0}gamma-final.dat'.format(args.outdir), gamma)

# Lazily reads a file batch_size lines at a time.
def batch_read(f, batch_size):
    lines = []
    for i in xrange(batch_size):
        try:
            lines.append(f.next())
        except StopIteration:
            return lines
    return lines

if __name__ == '__main__':
    main()
