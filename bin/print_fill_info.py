#!/usr/bin/env python

import argparse
import itertools
import os
import wbmtools.wbmutil as wbmutil

from wbmtools.wbmparser import WBMParser

wbmparser = WBMParser()

parser = argparse.ArgumentParser()
parser.add_argument('fills', help='comma-separated')

args = parser.parse_args()

def print_fill_info(fill):
    print('  fill:', fill)

    table = wbmutil.get_runs_for_fill(wbmparser, fill)
    print(*table[1].split(), sep='\n')


if __name__ == '__main__':
    fills = args.fills.split(',')

    for fill in fills:
        print_fill_info(fill)
