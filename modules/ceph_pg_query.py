#!/usr/bin/env python

import sys
import json
import argparse

""" Provide command line arguments """
parser = argparse.ArgumentParser(description='Query a specific pgid and print \
                                 the pg_stats from a given ceph-report. \
                                 Intended to provide similar functionality to \
                                 the ceph pg query command.')
parser.add_argument("--id",
                    dest="pgid",
                    required=True,
                    help="Specify a pgid to query from piped in ceph-report.")

args = parser.parse_args()

""" Print the pg_stats for the specific pgid that is being queried """
# Load in ceph-report json from stdin
obj = json.load(sys.stdin)

# Match the specified pgid with one from the ceph-report and print that portion
# of JSON only
for item in obj['pgmap']['pg_stats']:
    if item['pgid'] == str(args.pgid):
        print json.dumps(item, indent=4, sort_keys=True)
