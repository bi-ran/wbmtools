#!/usr/bin/env python

import argparse
import itertools
import os
import wbmtools.wbmutil as wbmutil

from wbmtools.wbmparser import WBMParser

wbmparser = WBMParser()

parser = argparse.ArgumentParser()
parser.add_argument('runs', nargs="+", help='run[:ls:ls]')
parser.add_argument('--paths', help='hlt paths')

args = parser.parse_args()

def print_l1_info(run_lumis, paths):
    run, lsmin, lsmax = run_lumis
    print('  run: ', run)

    table = wbmutil.get_lumis_summary(wbmparser, run)
    lumis = table[1:-1]

    header = [h.replace(' ', '') for h in table[0]]
    physics = header.index('Physics')
    b1pres = header.index('B1Pres')
    b2pres = header.index('B2Pres')

    lsphysics = filter(
        lambda l: l[physics] == l[b1pres] == l[b2pres] == 'GREEN', lumis[1:])
    lsfilter = list(filter(lambda l: int(l[1]) > 0, lsphysics))

    lslist = [int(l[0]) for l in lsfilter]
    lslim = [min(lslist), max(lslist)]

    lsmin = lslim[0] if lsmin is None else max(lslim[0], lsmin)
    lsmax = lslim[1] if lsmax is None else min(lslim[1], lsmax)
    print('   lumis: [{}, {}]\n'.format(lsmin, lsmax))

    linst = [float(l[3]) for l in lsfilter if lsmin <= int(l[0]) <= lsmax]
    avg_linst = sum(linst) / len(linst)
    print('   luminosity {:.2f}'.format(avg_linst))

    summary = wbmutil.get_l1_summary(wbmparser, run, lsmin, lsmax)

    if paths is None:
        paths = [*summary]

    for path in paths:
        if not path:
            print()
            continue

        try:
            line = summary[path]
            print('   {} {}'.format(path, ' '.join(line[2:-3])))
        except KeyError:
            print('   {} not found'.format(path))


def parse_run_lumis(run_lumis):
    run_lumis = run_lumis.split(':')

    if len(run_lumis) > 3:
        print('  truncating lumis')
    run_lumis = run_lumis[:3] + [None] * (3 - len(run_lumis))

    try:
        if any(map(int, run_lumis)) < 0:
            raise ValueError
    except ValueError:
        print('  invalid run/lumis')
        return None

    return [int(l) if l else None for l in run_lumis]


if __name__ == '__main__':
    paths = args.paths
    if paths is not None:
        paths = paths.split(',')

        if len(paths) == 1 and os.path.isfile(paths[0]):
            with open(paths[0]) as f:
                paths = f.read().splitlines()

    for run_lumis in args.runs:
        run_lumis = parse_run_lumis(run_lumis)

        if run_lumis is not None:
            print_l1_info(run_lumis, paths)
            print()
