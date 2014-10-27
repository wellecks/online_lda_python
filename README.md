online_lda_python
=================

Online LDA using Hoffman's Python Implementation.

Usage
```bash
$ python online_lda.py -h
usage: online_lda.py [-h] [-o OUTDIR] [-b BATCHSIZE] [-d NUM_DOCS]
                     [-k NUM_TOPICS] [-t TAU_0] [-l KAPPA] [-m MODEL_OUT_FREQ]
                     dataset vocab_file

positional arguments:
  dataset               Input dataset filename.
  vocab_file            Vocabulary filename.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        Directory to place output files. (default='')
  -b BATCHSIZE, --batchsize BATCHSIZE
                        Batch size. (default=256)
  -d NUM_DOCS, --num_docs NUM_DOCS
                        Total # docs in dataset. (default=7990787)
  -k NUM_TOPICS, --num_topics NUM_TOPICS
                        Number of topics. (default=100)
  -t TAU_0, --tau_0 TAU_0
                        Tau learning parameter to downweight early documents
                        (default=1024)
  -l KAPPA, --kappa KAPPA
                        Kappa learning parameter; decay factor for influence
                        of batches.(default=0.7)
  -m MODEL_OUT_FREQ, --model_out_freq MODEL_OUT_FREQ
                        Number of iterations interval for outputting a model
                        file. (default=10000)
```

Used in the blog post http://wellecks.wordpress.com/2014/10/26/ldaoverflow-with-online-lda/ 
