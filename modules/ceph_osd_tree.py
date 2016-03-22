#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE
from StringIO import StringIO
import simplejson as json

obj=json.load(sys.stdin)

itemById={}
bucketById={}
osdById={}
global dump_bucket_type
dump_bucket_type = 0

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

   #print bucketById

   print "  ID\t  Weight\t      Type\t        Name\t          Status\t         Reweight"
   for bucket in obj['crushmap']['buckets']:
      if bucket['type_name'] == 'root':
         outline = "{0:6d}\t".format(bucket['id'])
         if 'weight' in bucket:
            outline += "{0:8.4}\t".format(float(bucket['weight'])*0.00001526)

         outline += bucket['type_name']+" "
         outline += bucket['name']
         print outline
         dump_items(bucket)
 
osdtree()


