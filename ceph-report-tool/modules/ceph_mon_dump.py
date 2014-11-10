#!/usr/bin/env python
 
import sys
import simplejson as json
 
obj=json.load(sys.stdin)
epoch = str(obj['monmap']['epoch'])
print "dumped monmap epoch "+epoch
print "epoch "+epoch
print "fsid "+obj['monmap']['fsid']
print "last_changed "+obj['monmap']['modified']
print  "created "+obj['monmap']['created']

for mons in obj['monmap']['mons']:
	print str(mons['rank'])+":",
	print mons['addr'],
	print "mon."+mons['name']
