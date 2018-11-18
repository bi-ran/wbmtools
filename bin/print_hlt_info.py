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
    run, minls, maxls = run_lumis
    print('  run: ', run)

    lumis_summary = wbmutil.get_lumis_summary(wbmparser, run)

    lumis_filter = list(filter(lambda l: int(l[1]) > 0, lumis_summary[1:]))
    lumis_list = [int(l[0]) for l in lumis_filter]
    lumis_valid = [min(lumis_list), max(lumis_list)]

    minls = lumis_valid[0] if minls is None else max(lumis_valid[0], minls)
    maxls = lumis_valid[1] if maxls is None else min(lumis_valid[1], maxls)

    # clamp to (minls, maxls)
    pscol_for_lumis = {int(l[0]): int(l[1]) for l in lumis_filter
                       if minls <= int(l[0]) <= maxls}

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

    for lumis, pscol in subranges.items():
        if not pscol > 0:
            continue

        print()
        print('   lumis: [{}, {}], column: {}\n'.format(
            lumis[0], lumis[1], pscol))

        linst = [float(l[3]) for l in lumis_filter if
            lumis[0] <= int(l[0]) <= lumis[1]]
        avg_linst = sum(linst) / len(linst)
        print('   luminosity {:.2f}'.format(avg_linst))

        summary = wbmutil.get_hlt_summary(wbmparser, run, lumis[0], lumis[1])
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
