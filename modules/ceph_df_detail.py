#!/usr/bin/env python

import sys
import math
import simplejson as json

obj=json.load(sys.stdin)


def format_kbytes(b):
    if b > math.pow(1024,2):
        retval=b/math.pow(1024,2)
        retunit='G'
    elif b> 1024:
        retval=b/1024
        retunit='K'
    else:
        retval=b
        retunit=''

    return "{0:.0f}{1}".format(retval,retunit)

print "GLOBAL:"
print "    SIZE       AVAIL      RAW USED     %RAW USED     OBJECTS";
pg_stats_sum=obj['pgmap']['pg_stats_sum']['stat_sum'];
osd_stats_sum=obj['pgmap']['osd_stats_sum'];

print "    {0:<11}{1:<13}{2:<11}{3:>9.2f}  {4:>10}".format(
    format_kbytes(osd_stats_sum['kb']),
    format_kbytes(osd_stats_sum['kb_avail']),
    format_kbytes(osd_stats_sum['kb_used']),
    float(osd_stats_sum['kb_used'])/float(osd_stats_sum['kb'])*100,
    pg_stats_sum['num_objects'])

print ""

print "POOLS:"
print "    NAME                   ID     CATEGORY     USED     %USED     MAX AVAIL     OBJECTS     DIRTY     READ      WRITE";

pools={};

for pool in obj['osdmap']['pools']:
    if pool['type']==1:
        size=pool['size']
    else:
        size=float(pool['size'])/float(pool['min_size'])

    pools[pool['pool']]={
        'ID':pool['pool'],
        'NAME':pool['pool_name'],
        'MAXAVAIL':float(osd_stats_sum['kb_avail'])/float(size),
        }

outlines={};
for pool in obj['pgmap']['pool_stats']:
    outlines[pool['poolid']]="    {NAME:<23}{ID:<7}{CATEGORY:<5}{USED:>12}{PUSED:>10.2f}{MAXAVAIL:>14}{OBJECTS:>12}{DIRTY:>10}{READ:>10}{WRITE:>10}".format(
        NAME=pools[pool['poolid']]['NAME'],
        ID=pool['poolid'],
        CATEGORY='-',
        USED=format_kbytes(pool['stat_sum']['num_bytes']/1024),
        PUSED=(float(pool['stat_sum']['num_bytes'])/1024)/pools[pool['poolid']]['MAXAVAIL']*100,
        MAXAVAIL=format_kbytes(pools[pool['poolid']]['MAXAVAIL']),
        OBJECTS=pool['stat_sum']['num_objects'],
        DIRTY=pool['stat_sum']['num_objects_dirty'],
        READ=pool['stat_sum']['num_read'],
        WRITE=pool['stat_sum']['num_write']
        );


for outline in sorted(outlines):
    print outlines[outline]
