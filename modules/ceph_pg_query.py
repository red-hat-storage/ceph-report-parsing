#!/usr/bin/env python

import sys
import simplejson as json
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

""" Print the pg_stats for the specific that is being queried """
# Load in ceph-report json from stdin
obj=json.load(sys.stdin)
