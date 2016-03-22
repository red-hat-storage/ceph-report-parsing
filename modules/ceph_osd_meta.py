#!/usr/bin/env python

import json,sys
from StringIO import StringIO

obj=json.load(sys.stdin)

def osdmeta():
   osdmeta = obj['osd_metadata']
   print "  ID\t        IPP\t\t       IPC\t        Host\t          RAM\t         SWAP\t        Version\t      Kernel"
   for OSD in osdmeta:
        outline="{0:6d}\t".format(OSD['id'])
        outline += "{0:15}\t".format(OSD['front_addr'].split('/')[0])
        outline += "{0:15}\t".format(OSD['back_addr'].split('/')[0])
        outline += "{0:12}\t".format(OSD['hostname'])
        usep=float(OSD['mem_total_kb'])/float(1024.0);
        outline += "{0:6.0f} MB\t".format(usep)
        usep=float(OSD['mem_swap_kb'])/float(1024.0);
        outline += "{0:6.0f} MB\t".format(usep)
        outline += "{0:12}\t".format(OSD['ceph_version'].split(' ')[2])
        outline += "{0:36}\t".format(OSD['kernel_version'])
        print outline

osdmeta()

