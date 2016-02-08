#!/usr/bin/env python

import json,sys
from subprocess import Popen, PIPE
from StringIO import StringIO
from optparse import OptionParser

usage = "Usage: %prog [-f filename]"
parser = OptionParser()
parser.add_option("-f", "--file", action="store",type="string",dest="report",help="Use an input file rather than a ceph report command",default="")

(options, args) = parser.parse_args()

if (options.report != ''):
   r = Popen(['cat',options.report],stdout=PIPE,stderr=PIPE)
else:
   r = Popen(['ceph','report'],stdout=PIPE,stderr=PIPE)

cephreport, _ = r.communicate()

obj=json.load(StringIO(cephreport))

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

