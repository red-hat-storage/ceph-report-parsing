#!/usr/bin/env python

import sys
import simplejson as json

obj=json.load(sys.stdin)

print "  OSD\t        Size\t        Used\t       Avail\t  Use%"
for OSD in obj['pgmap']['osd_stats']:
	outline="{0:5d}\t".format(OSD['osd'])
	for i in [ 'kb', 'kb_used', 'kb_avail' ]:
		outline+="{0:12d}\t".format(OSD[i])
        if float(OSD['kb']) == 0.0: 
	   usep=0.0
        else:
	   usep=float(OSD['kb_used'])/float(OSD['kb'])*100;
	print outline+"{0:6.2f}".format(usep)


