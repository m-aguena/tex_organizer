#!/usr/bin/env python
from __future__ import print_function

break_line = ['@','%-','% *']

def flat(bib, bibf, bibs, field):

    d_in = bib
    d_ou = bibf

    print('%s -> %s'%(d_in.split('/')[-1], d_ou.split('/')[-1]))
    
    data = open(d_in,'r').readlines()
    newdata = []
    for d in data:
      if d != '\n':
        line = ' '.join(d.split('\t'))
        line = d.split(' ')
        newdata.append( ' '.join([i for ind,i in enumerate(line) if ((i!='') or ((i=='')and(i!=line[ind-1]) ))])[:-1] )
    
    out = open(d_ou,'w')
    for l in newdata:
      if len(l)>0:
        for symb in break_line:
            if l[:len(symb)] == symb:
                print('',file=out)
        print(l,file=out,end='')
    out.close()

def un_flat(bib, bibf, bibs, field):

    d_in = bibf
    d_ou = bib

    print('%s -> %s'%(d_in.split('/')[-1], d_ou.split('/')[-1]))
    
    data = open(d_in,'r').readlines()
    types = []
    for d in data:
        line = d.split(',')
        for el0 in line:
            el = el0.split('=')
            if len(el)>1:
                types.append(''.join(el[0].split(' ')))
    
    types = set(types)
    lens = max([len(t) for t in types])
    LEN = dict([[t,lens-len(t)] for t in types])
    
    '''
    print(types,lens)
    for t in types:
        print (t,len(t))
    '''
    
    newdata = []
    for d in data:
        line = d.split(',')
        out = line[0]
        if len(line)>1:
            for el in line[1:]:
                ext = ','
                if len(el.split('='))>1:
                    ext = ',\n'+''.join([' ' for i in range( LEN[''.join(el.split('=')[0].split(' '))] )])
                out += ext
                if el==line[-1]: 
                    el = el[:-2]+'\n'+el[-2:]
                if len(el.split('='))>1:
                    while el[0]==' ': el = el[1:]
                out += el
        newdata.append(out)
    
    
    out = open(d_ou,'w')
    for l in newdata:
        print(l,file=out,end='')
    out.close()

def resort(bib, bibf, bibs, field):

    d_in = bibf
    d_ou = bibs

    import os

    if not os.path.isfile(d_in):
        flat(bib, bibf, bibs)

    print('%s -> %s'%(d_in.split('/')[-1], d_ou.split('/')[-1]))
    
    data = open(d_in,'r').readlines()
    DIC = []
    for d in data:
        line = d.split(',')
        if len(line)>1:
            if line[1][1:7]=='author':
                name = ''.join(line[1].split('=')[1].split(' '))
                name = ''.join(name.split('{'))
                name = ''.join(name.split('}'))
                name = ''.join(name.split('"'))
                #DIC.append([name,line[0]+''.join([' ' for i in range(40-len(line[0]))])+','+','.join(line[1:-1])+'}'])
                it = 0
                for i,l in enumerate(line):
                    #if l[1:6]=='title': it = i
                    if field in l:it = i
                DIC.append([name,line[0]+''.join([' ' for i in range(40-len(line[0]))])+','+line[it]+'}'])
    
    DIC = sorted(DIC,key = lambda DIC:DIC[0] )
    leng=len(DIC)-1
    
    prt_all = False
    prt_all = True

    def cond(d,i,title=False):
        if prt_all:
            if title: return (d[0]!=DIC[i-1][0])
            else: return True
        if title and i<leng:
            return (d[0]!=DIC[i-1][0]) and (d[0]==DIC[i+1][0])
        else:
            if i<leng:
                return (d[0]==DIC[i-1][0]) or (d[0]==DIC[i+1][0])
            else:
                return DIC[-1][0]==DIC[-2][0]

    out = open(d_ou,'w')
    #for d in DIC:
    for i,d in enumerate(DIC):
        if cond(d,i,True):
            print('\n%%%%',d[0],'%%%%%%%%%%',file=out)
        if cond(d,i):
            print(DIC[i][1][1:],file=out)
    out.close()

funcs = {'f':flat,'u':un_flat,'s':resort}

def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', metavar='N', nargs=1,help='name of bib file')
    parser.add_argument('-t','--type',dest='typ',default='f',help='select function: flatten(f), unflatten(u) or sort(s)')
    parser.add_argument('-f','--field',dest='field',default='title',help='select field for sorted bib')

    bib  = parser.parse_args().fname[0]
    bibv = bib.split('.')
    bibf = '.'.join(bibv[:-1]+['flat',bibv[-1]])
    bibs = '.'.join(bibv[:-1]+['sort',bibv[-1]])


    func = funcs[ parser.parse_args().typ ]

    func(bib, bibf, bibs, parser.parse_args().field )

if __name__=='__main__':

    run()
