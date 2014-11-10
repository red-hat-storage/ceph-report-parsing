#!/usr/bin/env python
 
import sys
import simplejson as json
 
obj=json.load(sys.stdin)
 
print obj['health']['overall_status'],
for summary in obj['health']['summary']:
	print summary['summary']+";",
