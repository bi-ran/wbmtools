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

def print_hlt_info(run_lumis, paths):
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

    # clamp to (lsmin, lsmax)
    pscol_for_lumis = {int(l[0]): int(l[1]) for l in lsfilter
                       if lsmin <= int(l[0]) <= lsmax}

    # divide into lumi sections
    subranges = {(a[0][0], a[-1][0]): a[0][1] for a in [
        list(g) for k, g in itertools.groupby(
            pscol_for_lumis.items(), key=lambda x: x[1])]}

    # retrieve hlt prescale columns
    key = wbmutil.get_run_summary(wbmparser, run)['key']
    hltps = wbmutil.get_prescale_columns(wbmparser, key)

    # retrieve l1 prescale sets
    l1ps = wbmutil.get_prescale_sets(wbmparser, run)
    l1ps = {l[1]: l[2:] for l in l1ps[1:] if l[1]}

    for ls, pscol in subranges.items():
        if not pscol > 0:
            continue

        print()
        print('   lumis: [{}, {}], column: {}\n'.format(ls[0], ls[1], pscol))

        linst = [float(l[3]) for l in lsfilter if ls[0] <= int(l[0]) <= ls[1]]
        avg_linst = sum(linst) / len(linst)
        print('   luminosity {:.2f}'.format(avg_linst))

        summary = wbmutil.get_hlt_summary(wbmparser, run, ls[0], ls[1])
        summary.pop('Name', None)

        if paths is None:
            paths = [*summary]

        for path in paths:
            if not path:
                print()
                continue

            try:
                pathps = hltps[path]
                totalps = (int(pathps[pscol]) * int(l1ps[pathps[-1]][pscol]))
                line = summary[path]
                print('   {} {} {} {} {} {}'.format(
                    path, int(line[5]), float(summary[path][6]),
                    int(line[3]), int(line[4]), totalps))
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
            print_hlt_info(run_lumis, paths)
            print()
