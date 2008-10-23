# Python

# Extracts rst function comments and dumps them to a file

import sys
import os
import re
import urllib2
import urlparse

if len(sys.argv)!=3:
    print >> sys.stderr, "You must supply input and output filenames"

if os.path.exists(sys.argv[2]):
    os.remove(sys.argv[2])

op=[]
op.append(".. Automatically generated by code2rst.py")
op.append("   code2rst.py %s %s" % (sys.argv[1], sys.argv[2]))
op.append("   Edit %s not this file!" % (sys.argv[1],))
op.append("")
if sys.argv[1]!="src/apsw.c":
    op.append(".. currentmodule:: apsw")
    op.append("")

funclist={}
def do_funclist():
    baseurl="http://www.sqlite.org/c3ref/funclist.html"
    page=urllib2.urlopen(baseurl).read()
    funcs=re.findall(r"""<a href="([^'"]+?/c3ref/[^<]+?\.html)['"]>(sqlite3_.+?)<""", page)
    for relurl,func in funcs:
        funclist[func]=urlparse.urljoin(baseurl, relurl)
        # ::TODO:: consider grabbing the page and extracting first <h2> to get
        # description of sqlite3 api

# we have our own markup to describe what sqlite3 calls we make using
# -* and then a space seperated list.  Maybe this could just be
# automatically derived from the source?
def do_calls(line):
    line=line.strip().split()
    assert line[0]=="-*"
    indexop=["", ".. index:: "+(", ".join(line[1:])), ""]
    saop=["", "  Calls:"]
    for func in line[1:]:
        saop.append("    * `%s <%s>`_" % (func, funclist[func]))
    saop.append("")
    return indexop, saop
             

def do_methods():
    keys=methods.keys()
    keys.sort()

    for k in keys:
        op.append("")
        d=methods[k]
        dec=d[0]
        d=d[1:]
        indexop=[]
        saop=[]
        newd=[]
        for line in d:
            if line.strip().startswith("-*"):
                indexop, saop=do_calls(line)
            else:
                newd.append(line)

        d=newd

        # insert index stuff
        op.extend(indexop)
        # insert classname into dec
        dec=re.sub(r"^(\.\.\s+method::\s+)()", r"\1"+curclass+".", dec)
        op.append(dec)
        op.extend(d)
        op.append("")
        op.extend(saop)



do_funclist()

methods={}

curop=[]

cursection=None

incomment=False
curclass=None

for line in open(sys.argv[1], "rtU"):
    line=line.rstrip()
    if not incomment and line.lstrip().startswith("/**"):
        # a comment intended for us
        line=line.lstrip(" \t/*")
        cursection=line
        incomment=True
        assert len(curop)==0
        t=line.split()[1]
        if t=="class::":
            if methods:
                do_methods()
                methods={}
            curclass=line.split()[2].split("(")[0]
        curop.append(line)
        continue
    # end of comment
    if incomment and line.lstrip().startswith("*/"):
        incomment=False
        line=cursection
        t=cursection.split()[1]
        if t=="method::":
            name=line.split()[2].split("(")[0]
            methods[name]=curop
        elif t=="class::":
            op.append("")
            op.append(curclass+" class")
            op.append("="*len(op[-1]))
            op.append("")
            op.extend(curop)
        else:
            op.extend(curop)
            
        curop=[]
        continue
    # ordinary comment line
    if incomment:
        curop.append(line)
        continue

    # ignore everything else


if methods:
    do_methods()

open(sys.argv[2], "wt").write("\n".join(op)+"\n")