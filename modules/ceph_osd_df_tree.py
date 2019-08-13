#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE
from StringIO import StringIO
import json as json

obj=json.load(sys.stdin)

itemById={}
bucketById={}
osdById={}
osdSizes={}
global dump_bucket_type
dump_bucket_type = 0

def get_sizes():
    for OSD in obj['pgmap']['osd_stats']:
        osdSizes[OSD['osd']]={}
        osdSizes[OSD['osd']]['pgs']=0
        for i in [ 'kb', 'kb_used', 'kb_avail' ]:
            osdSizes[OSD['osd']][i]=OSD[i]
            if float(OSD['kb']) == 0.0: 
                usep=0.0
            else:
               usep=float(OSD['kb_used'])/float(OSD['kb'])*100;
            osdSizes[OSD['osd']]['usep']=usep

def get_pgs():
    for pg in obj['pgmap']['pg_stats']:
        for osdIndex in range(0,len(pg['acting'])):
            osdSizes[pg['acting'][osdIndex]]['pgs']+=1

def dump_items(b):
   global dump_bucket_type
   dump_bucket_type += 1
   for osd in obj['osdmap']['osds']:
      osdById[osd['osd']] = osd

   for i in b['items']:
      index = 0
      if i['id'] > -1:
         outline = "{0:6d}\t".format(i['id'])
         outline += "{0:8.4}\t".format(float(i['weight'])*0.00001526)
         while index < dump_bucket_type:
            outline += '\t'
            index += 1
         outline += "osd."+str(i['id'])+"\t\t\t   "
         if i['id'] in osdById:
            if osdById[i['id']]['up']  == 1:
               outline += "up/"
            else:
               outline += "down/"
            if osdById[i['id']]['in']  == 1:
               outline += "in\t"
            else:
               outline += "out\t"
            if 'weight' in osdById[i['id']]:
               outline += "{0:4.3}".format(osdById[i['id']]['weight'])
         else:
            outline += "\tunknown"
         outline+="{0:4d}\t".format(osdSizes[i['id']]['pgs'])
         for field in ['kb','kb_used','kb_avail']:
            outline+="{0:12d}\t".format(osdSizes[i['id']][field])
         outline+="{0:6.2f}".format(osdSizes[i['id']]['usep'])
         print outline
      else:
         cb = bucketById[i['id']]
         outline = "{0:6d}\t".format(cb['id'])
         if 'weight' in cb:
            outline += "{0:8.4}\t".format(float(cb['weight'])*0.00001526)
         while index < dump_bucket_type:
            outline += '\t'
            index += 1
         outline += cb['type_name']+" "
         outline += cb['name']
         print outline

         dump_items(cb)
         dump_bucket_type -= 1

def osdtree():
   dump_bucket_type = 0
   for bucket in obj['crushmap']['buckets']:
           bucketById[bucket['id']]=bucket

   print "  ID\t  Weight\t      Type\t        Name\t          Status    Reweight   PGs\t    Size\t        Used\t       Avail\t Use %"
   for bucket in obj['crushmap']['buckets']:
      if bucket['type_name'] == 'root':
         outline = "{0:6d}\t".format(bucket['id'])
         if 'weight' in bucket:
            outline += "{0:8.4}\t".format(float(bucket['weight'])*0.00001526)

         outline += bucket['type_name']+" "
         outline += bucket['name']
         print outline
         dump_items(bucket)

get_sizes() 
get_pgs()
osdtree()
