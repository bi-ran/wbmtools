#!/usr/bin/env python

import argparse
import itertools
import os
import wbmtools.wbmutil as wbmutil

from wbmtools.wbmparser import WBMParser

wbmparser = WBMParser()

def get_int_lumi(run_lumis):
    run, lsmin, lsmax = run_lumis

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
    if not lslist:
        return 0.

    lslim = [min(lslist), max(lslist)]

    lsmin = lslim[0] if lsmin is None else max(lslim[0], lsmin)
    lsmax = lslim[1] if lsmax is None else min(lslim[1], lsmax)

    return sum([float(l[3]) * (1. - float(l[6])/100)
        for l in lsfilter if lsmin <= int(l[0]) <= lsmax])


def parse_run_lumis(run):
    run_lumis = run.split(':')

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


def main(runs, fills):
    if runs is not None:
        lint = 0.
        for run in runs:
            run_lumis = parse_run_lumis(run)

            if run_lumis is not None:
                lint += get_int_lumi(run_lumis)

        print('   run {} luminosity {:.1f}'.format(run, lint))

    elif fills is not None:
        for fill in fills.split(','):
            table = wbmutil.get_runs_for_fill(wbmparser, fill)
            runs = map(int, table[1].split())

            lint = 0.
            for run in runs:
                lint += get_int_lumi([run, None, None])

            print('   fill {} luminosity {:.1f}'.format(fill, lint))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('runs', nargs="?", help='run[:ls:ls]')
    parser.add_argument('-f', '--fills', help='comma-separated')

    args = parser.parse_args()

    main(args.runs, args.fills)
