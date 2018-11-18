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
    run, minls, maxls = run_lumis
    print('  run: ', run)

    lumis = wbmutil.get_lumis_summary(wbmparser, run)

    lumis_filter = list(filter(lambda l: int(l[1]) > 0, lumis[1:]))
    lumis_list = [int(l[0]) for l in lumis_filter]
    lumis_valid = [min(lumis_list), max(lumis_list)]

    minls = lumis_valid[0] if minls is None else max(lumis_valid[0], minls)
    maxls = lumis_valid[1] if maxls is None else min(lumis_valid[1], maxls)
    print('   lumis: [{}, {}]\n'.format(minls, maxls))

    linst = [float(l[3]) for l in lumis_filter if minls <= int(l[0]) <= maxls]
    avg_linst = sum(linst) / len(linst)
    print('   luminosity {:.2f}'.format(avg_linst))

    summary = wbmutil.get_l1_summary(wbmparser, run, minls, maxls)

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
