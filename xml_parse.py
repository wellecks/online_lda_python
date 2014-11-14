# Reads an XML file, parses specified fields into a string,
# and outputs to a file.
#
# python xml_parse.py --help for info on cmd line arguments.

import re
import xml.etree.cElementTree as ET
import argparse

from printer import Printer

argparser = argparse.ArgumentParser()
argparser.add_argument("-i", "--input", dest="xml_file", help="XML input filename.")
argparser.add_argument("-o", "--output", dest="outfile", help="Output text filename.")
argparser.add_argument("-t", "--tag", dest="tag", default="row", help="XML tag to parse.")
argparser.add_argument("-f", "--fields", dest="fields", default=['Title', 'Body', 'Tags'], nargs="+", help="XML fields to parse.")
argparser.add_argument("-n", "--num_records", dest="num_records", type=int, default=27000000, help="Approx # lines in xml_file.")
argparser.add_argument("-s", "--num_samples", dest="num_samples", type=int, default=-1, help="Number of samples. If greater than zero, will sample file instead of parsing entire file.")
args = argparser.parse_args()

# regular expressions
HTML_TAG_RE = re.compile(r'<[^>]+>')
TAG_RE = re.compile("<|>")
ALPHANUM_RE = re.compile(r'[^a-zA-Z0-9\s]')
ALPHA_RE = re.compile(r'[^a-zA-Z\s]')

STOP_WORDS = "ive,gt,lt,a,able,about,above,abst,accordance,according,accordingly,across,act,actually,added,adj,affected,affecting,affects,after,afterwards,again,against,ah,all,almost,alone,along,already,also,although,always,am,among,amongst,an,and,announce,another,any,anybody,anyhow,anymore,anyone,anything,anyway,anyways,anywhere,apparently,approximately,are,aren,arent,arise,around,as,aside,ask,asking,at,auth,available,away,awfully,b,back,be,became,because,become,becomes,becoming,been,before,beforehand,begin,beginning,beginnings,begins,behind,being,believe,below,beside,besides,between,beyond,biol,both,brief,briefly,but,by,c,ca,came,can,cannot,can't,cause,causes,certain,certainly,co,com,come,comes,contain,containing,contains,could,couldnt,d,date,did,didn't,different,do,does,doesn't,doing,done,don't,down,downwards,due,during,e,each,ed,edu,effect,eg,eight,eighty,either,else,elsewhere,end,ending,enough,especially,et,et-al,etc,even,ever,every,everybody,everyone,everything,everywhere,ex,except,f,far,few,ff,fifth,first,five,fix,followed,following,follows,for,former,formerly,forth,found,four,from,further,furthermore,g,gave,get,gets,getting,give,given,gives,giving,go,goes,gone,got,gotten,h,had,happens,hardly,has,hasn't,have,haven't,having,he,hed,hence,her,here,hereafter,hereby,herein,heres,hereupon,hers,herself,hes,hi,hid,him,himself,his,hither,home,how,howbeit,however,hundred,i,id,ie,if,i'll,im,immediate,immediately,importance,important,in,inc,indeed,index,information,instead,into,invention,inward,is,isn't,it,itd,it'll,its,itself,i've,j,just,k,keep,keeps,kept,kg,km,know,known,knows,l,largely,last,lately,later,latter,latterly,least,less,lest,let,lets,like,liked,likely,line,little,'ll,look,looking,looks,ltd,m,made,mainly,make,makes,many,may,maybe,me,mean,means,meantime,meanwhile,merely,mg,might,million,miss,ml,more,moreover,most,mostly,mr,mrs,much,mug,must,my,myself,n,na,name,namely,nay,nd,near,nearly,necessarily,necessary,need,needs,neither,never,nevertheless,new,next,nine,ninety,no,nobody,non,none,nonetheless,noone,nor,normally,nos,not,noted,nothing,now,nowhere,o,obtain,obtained,obviously,of,off,often,oh,ok,okay,old,omitted,on,once,one,ones,only,onto,or,ord,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,owing,own,p,page,pages,part,particular,particularly,past,per,perhaps,placed,please,plus,poorly,possible,possibly,potentially,pp,predominantly,present,previously,primarily,probably,promptly,proud,provides,put,q,que,quickly,quite,qv,r,ran,rather,rd,re,readily,really,recent,recently,ref,refs,regarding,regardless,regards,related,relatively,research,respectively,resulted,resulting,results,right,run,s,said,same,saw,say,saying,says,sec,section,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sent,seven,several,shall,she,shed,she'll,shes,should,shouldn't,show,showed,shown,showns,shows,significant,significantly,similar,similarly,since,six,slightly,so,some,somebody,somehow,someone,somethan,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specifically,specified,specify,specifying,still,stop,strongly,sub,substantially,successfully,such,sufficiently,suggest,sup,sure,than,that,that's,the,their,theirs,them,themselves,then,there,there's,these,they,they'd,they'll,they're,they've,this,those,through,to,too,under,until,up,very,was,wasn't,we,we'd,we'll,we're,we've,were,weren't,what,what's,when,when's,where,where's,which,while,who,who's,whom,why,why's,with,won't,would,wouldn't,you,you'd,you'll,you're,you've,your,yours,yourself,yourselves".split(',')

# @param tokens : list of lower-cased tokens
# @return       : list of lower-cased tokens without stop word tokens
def remove_stopwords(tokens):
    return filter(lambda t: t not in STOP_WORDS, tokens)

# @param text : a string of text
# @return     : a string of text
def clean(text):
    clean_tokens = ALPHA_RE.sub('', HTML_TAG_RE.sub('', text)).strip().split()
    clean_tokens = [t.lower() for t in clean_tokens]
    clean_tokens = remove_stopwords(clean_tokens)
    return ' '.join(clean_tokens)

# Parse tag values; specific to StackOverflow dataset.
# @param tag_text : a string of text of the form "<tag><tag>..."
# @return         : list of tag tokens
def parse_tags(tag_text):
    return filter(lambda x: x != '', TAG_RE.split(tag_text))

# Parses all lines of the input xml_file and writes result to outfile.
# @param xml_file : input xml filename
# @param outfile  : output xml filename
# @param fields   : xml fields / attributes to parse for each tag
# @param tag      : xml tag to parse; e.g. identifies a row
# @param n        : estimated number of xml rows used for progress estimation.
# @param interval : only process lines on the interval. 1 means process every line.
def parse_and_write(xml_file, outfile, fields, tag, n, interval=1):
    # get an iterable
    context = ET.iterparse(xml_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    i = 0
    with open(outfile, 'w') as f:
        for event, row in context:
            if event == "end" and row.tag == tag:
                if i % 100000 == 0:
                    pct = round((i * 1.0 / n) * 100, 1)
                    Printer("Processed {0} records. ~ {1}\% complete.".format(i, pct))
                if interval == 1 or i % interval == 0:
                    if all(map(lambda x: x in row.attrib, fields)):
                        field_data = []
                        for fd in fields:
                            if fd == 'Tags':
                                field_data.extend(parse_tags(row.attrib[fd].encode('ascii', 'ignore')))
                            else:
                                field_data.append(clean(row.attrib[fd].encode('ascii', 'ignore')))
                        text = " ".join(field_data) + "\n"
                        f.write(text)
                i += 1
                root.clear()
                if i >= n:
                    break

# Parses n_samples lines from the input xml_file. Lines with
# index satisfying i % (n_records / n_samples) are chosen.
def sample(xml_file, outfile, fields, tag, n_samples, n_records):
    index_interval = n_records / n_samples
    parse_and_write(xml_file, outfile, fields, tag, n_records, index_interval)

if args.num_samples > 0:
    sample(args.xml_file, args.outfile, args.fields, args.tag, args.num_samples, args.num_records)
else:
    parse_and_write(args.xml_file, args.outfile, args.fields, args.tag, args.num_records)