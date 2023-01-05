#!/usr/bin/env python
from __future__ import print_function

break_line = ['@','%-','% *', '%%%%']

def flatten(data):
    
    newdata = ['']
    for d in data:
        if d != '\n':
            line = d.replace('\t', '')

            size = len(line)
            line = line.replace('  ', ' ')
            line = line.replace('\n', '')
            while len(line)!=size:
                size = len(line)
                line = line.replace('  ', ' ')
            if any(line[:len(symb)]==symb for symb in break_line):
                newdata.append('')
            newdata[-1] += line
    
    return newdata

def sort_data_w_keys(data, field='author'):

    sorted_data = []
    for d in data:
        if len(d)>0:
            line = d.split(',')
            if len(line)>1:
                if line[1][1:len(field)+1]==field:
                    key = line[1].split('=')[1].replace(' ', '').replace('{', '').replace('}', '').replace('"', '')
                    sorted_data.append([key, d])
    
    return sorted(sorted_data, key = lambda DIC:DIC[0])

def sort_data(data, field='author', field_separation=False):

    sorted_data = []
    current_key = ''
    for key, data in sort_data_w_keys(data, field):
        if key!=current_key and field_separation:
            sorted_data.append(f'\n%%%% {key} %%%%%%%%%%')
            current_key = key
        sorted_data.append(data)

    return sorted_data

def get_info_dict(line):
    out = {}
    key = None
    for part in line.replace('\n', '')[:-1].split(',')[1:]: # -2 to remove last "}\n"
        if len(part.split('='))>1:
            if key is not None:
                out[key] += ','
            key = part.split('=')[0].replace(' ', '')
            out[key] = part.split('=')[1]
        else:
            out[key] += f',{part}'
    return out

    
def unflatten(data):

    # find right spacing

    types = []
    for line in data:
        for element in line.split(','):
            if '=' in element:
                types.append(element.split('=')[0].replace(' ', ''))
    
    types = set(types)
    len_max = max([len(t) for t in types])
    len_space = dict([[t, len_max-len(t)] for t in types])
    
    # prep data

    new_data = []
    for line in data:
        if all(s in line for s in ',='):
            new_data.append(f"{line.split(',')[0]},")
            for key, value in get_info_dict(line).items():
                new_data.append(' '*len_space[key]+f'{key} ={value}')
            new_data.append('}')
        else:
            new_data.append(line)

    return new_data

def complete_sort(data, field='author', field_separation=False):
    data_flat = flatten(data)
    data_sorted = sort_data(data_flat, field, field_separation)
    return unflatten(data_sorted)


# file functions

def save_file(data, filename):
    out = open(filename,'w')
    print('\n'.join(data), file=out)
    out.close()

def flatten_file(org_file, out_file):

    print('%s -> %s'%(org_file.split('/')[-1], out_file.split('/')[-1]))
    
    data = flatten(open(org_file,'r').readlines())
    save_file(data, out_file)


def sort_file(flat_file, out_file, field='author'):

    print('%s -> %s'%(flat_file.split('/')[-1], out_file.split('/')[-1]))

    data = sort_data(open(flat_file,'r').readlines(), field, field_separation=True)
    save_file(data, out_file)


def unflatten_file(flat_file, out_file):

    print('%s -> %s'%(flat_file.split('/')[-1], out_file.split('/')[-1]))

    data = unflatten(open(flat_file,'r').readlines())
    save_file(data, out_file)

def complete_sort_file(org_file, out_file, field='author'):

    print('%s -> %s'%(org_file.split('/')[-1], out_file.split('/')[-1]))

    data = complete_sort(open(org_file,'r').readlines(), field, field_separation=True)
    save_file(data, out_file)

#funcs = {'f':flatten,'u':un_flat,'s':resort}

def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', metavar='N', nargs=1, help='name of bib file')
    parser.add_argument('-t', '--type', dest='typ', default='c', 
                        help='select function: flatten(f), unflatten sorted (u), sort(s) or complete run (c)')
    parser.add_argument('-f', '--field', dest='field', default='author', help='select field for sorted bib')

    bib  = parser.parse_args().fname[0]
    bibv = bib.split('.')
    bibf = '.'.join([*bibv[:-1], 'flat', bibv[-1]])
    bibs = '.'.join([*bibv[:-1], 'sort', bibv[-1]])
    bibr = '.'.join([*bibv[:-1], 'final', bibv[-1]])

    fkwargs = {'field': parser.parse_args().field}

    func, args, kwargs = {
        'f': (flatten_file, [bib, bibf], {}),
        's': (sort_file, [bibf, bibs], fkwargs),
        'u': (unflatten_file, [bibs, bibr], {}),
        'c': (complete_sort_file, [bib, bibr], fkwargs),
        }[parser.parse_args().typ]


    func(*args, **kwargs)


if __name__=='__main__':

    run()
