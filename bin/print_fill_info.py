#!/usr/bin/env python

import argparse
import itertools
import os
import wbmtools.wbmutil as wbmutil

from wbmtools.wbmparser import WBMParser

wbmparser = WBMParser()

def print_fill_info(fill):
    print('  fill:', fill)

    table = wbmutil.get_runs_for_fill(wbmparser, fill)
    print(*table[1].split(), sep='\n')


def main(fills):
    for fill in fills.split(','):
        print_fill_info(fill)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fills', help='comma-separated')

    args = parser.parse_args()

    main(args.fills)
